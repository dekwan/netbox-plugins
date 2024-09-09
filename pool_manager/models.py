import random

from django.core.validators import RegexValidator
from django.db import models
from django.urls import reverse
from netbox.models import NetBoxModel


class AlgorithmChoices(models.TextChoices):
    FIRST_AVAILABLE = u'first_available', 'First Available'
    ROUND_ROBIN = u'round_robin', 'Round Robin'
    RANDOM = u'random', 'Random'

class Pool(NetBoxModel):
    name = models.CharField(
        max_length=100,
        unique=True,
        blank=False,
        help_text="The name of the pool."
    )
    description = models.CharField(
        max_length=200,
        blank=False,
        help_text="A brief description of the pool."
    )
    range = models.CharField(
        max_length=200,
        blank=False,
        validators=[
            RegexValidator(
                regex=r'^((\s*\d+\s*)+(-\s*\d+\s*)?)(,((\s*\d+\s*)+(-\s*\d+\s*)?))*$',
                message="Enter a valid range.",
                code="invalid_range",
            ),
        ],
        help_text="The range(s) of the pool in the format of integer or integer-integer and separated by a comma. ie. 1-10, 20-30, 35, 40"
    )
    algorithm = models.CharField(
        max_length=50,
        blank=False,
        choices=AlgorithmChoices.choices,
        default=AlgorithmChoices.FIRST_AVAILABLE,
        help_text="The type of algorithm to pull from the pool."
    )
    index = models.PositiveIntegerField(
        blank=True,
        default=0,
        help_text="The current index of the pool (for round robin)."
    )

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('plugins:pool_manager:pool', args=[self.pk])
    
    def get_pool_lease_details(self):
        range_list = Pool.get_range_as_list(self.range)
        pool_size = len(range_list)
        existing_pool_lease_list = PoolLease.get_pool_lease_range_numbers(self.id)
        in_use = len(existing_pool_lease_list)

        return pool_size, in_use, (pool_size - in_use)
    
    def get_pool_by_name(pool_name):
        return Pool.objects.get(name=pool_name)
    
    def get_pool_by_id(pool_id):
        return Pool.objects.get(id=pool_id)
    
    def get_range_as_list(range_str):
        try:
            pool_range_list = range_str.replace(' ', '').split(',')

            pool_range_as_list = []
            for pool_range_str in pool_range_list:
                pool_range_str_as_list = pool_range_str.split('-')
                start_range = int(pool_range_str_as_list[0])
                if(len(pool_range_str_as_list) == 1):
                    end_range = start_range
                else:
                    end_range = int(pool_range_str_as_list[1])
                
                # Invalid range
                if start_range > end_range:
                    return None

                for range_number in range(start_range, end_range+1):
                    pool_range_as_list.append(range_number)

            # Remove duplicate values
            pool_range_as_list = list(set(pool_range_as_list))

            pool_range_as_list.sort()
            
            return pool_range_as_list
        except Exception:
            return None

class PoolLease(NetBoxModel):
    pool = models.ForeignKey(
        to=Pool,
        on_delete=models.PROTECT,
        related_name='lease_to_pool',
        blank=False
    )
    requester_id = models.CharField(
        max_length=200,
        blank=False,
        help_text="The id of the requester."
    )
    requester_details = models.CharField(
        max_length=200,
        blank=True,
        help_text="A brief description of the purpose of the lease."
    )
    range_number = models.PositiveIntegerField(
        blank=False,
        help_text="The range number assigned to the lease in the pool."
    )
    tag = models.CharField(
        max_length=200,
        blank=True,
        help_text="A tag to categorize the pool lease."
    )

    class Meta:
        ordering = ('pool', 'range_number')
        unique_together = ('pool', 'range_number')

    def __str__(self):
        return f'Pool: {self.pool}, Range Number {self.range_number}'

    def get_absolute_url(self):
        return reverse('plugins:pool_manager:poollease', args=[self.pk])
    
    def get_pool_lease(lease_id):
        return PoolLease.objects.get(id=lease_id)
    
    def get_pool_lease_range_numbers(pool_id):
        return list(PoolLease.objects.filter(pool=pool_id).values('range_number').values_list('range_number', flat=True))    

    def get_lease_range_number(pool_id):
        pool = Pool.get_pool_by_id(pool_id)
        pool_range_list = Pool.get_range_as_list(pool.range)
        if pool_range_list == None:
            return None

        existing_range_numbers_list = PoolLease.get_pool_lease_range_numbers(pool_id)
        
        algorithm = pool.algorithm
        if algorithm == AlgorithmChoices.FIRST_AVAILABLE:
            for range_number in pool_range_list:
                if existing_range_numbers_list.count(range_number) == 0:
                    return range_number
        elif algorithm == AlgorithmChoices.ROUND_ROBIN:
            index = pool.index
            
            for i in range(0, len(pool_range_list)):
                if index >= len(pool_range_list):
                    # Need to go back to the front of the array
                    index = 0

                range_number = pool_range_list[index]

                # Go to the next index
                index += 1
                
                if existing_range_numbers_list.count(range_number) == 0:
                    pool.index = index
                    pool.save()
                    return range_number
        elif algorithm == AlgorithmChoices.RANDOM:
            # Create a list that contains range numbers that are available
            available_range_numbers = pool_range_list.copy()
            for range_number in existing_range_numbers_list:
                available_range_numbers.remove(range_number)
            
            # Select a random range_number
            random_range_number = random.choice(available_range_numbers)
            return random_range_number

        return None