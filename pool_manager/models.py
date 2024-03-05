from django.core.validators import RegexValidator
from django.db import models
from django.urls import reverse

from django.http import HttpResponseBadRequest

from netbox.models import NetBoxModel


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
                regex=r'^((\s*\d+\s*)(-\s*\d+\s*)?(,)?)+$',
                message="Enter a valid range.",
                code="invalid_range",
            ),
        ],
        help_text="The range(s) of the pool in the format of integer or integer-integer and separated by a comma. ie. 1-10, 20-30, 35, 40"
    )

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('plugins:pool_manager:pool', args=[self.pk])
    
    def get_pool_by_name(pool_name):
        return Pool.objects.get(name=pool_name)
    
    def get_pool_by_id(pool_id):
        return Pool.objects.get(id=pool_id)
    
    def get_range_as_tuple_list(pool_id):
        pool_range_list = Pool.get_pool_by_id(pool_id).range.replace(' ', '').split(',')
        
        pool_range_tuple_list = []
        for pool_range_str in pool_range_list:
            pool_range_str_as_list = pool_range_str.split('-')
            start_range = int(pool_range_str_as_list[0])
            if(len(pool_range_str_as_list) == 1):
                end_range = start_range
            else:
                end_range = int(pool_range_str_as_list[1])
            pool_range_tuple_list.append((start_range, end_range))
        
        pool_range_tuple_list.sort()

        return pool_range_tuple_list


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

    class Meta:
        ordering = ('pool', 'range_number')
        unique_together = ('pool', 'range_number')

    def __str__(self):
        return f'{self.pool}: Range Number {self.range_number}'

    def get_absolute_url(self):
        return reverse('plugins:pool_manager:poollease', args=[self.pk])
    
    def get_pool_lease(lease_id):
        return PoolLease.objects.get(id=lease_id)
    
    def get_pool_lease_range_numbers(pool_id):
        return list(PoolLease.objects.filter(pool=pool_id).values('range_number').values_list('range_number', flat=True))
    
    def get_lease_range_number(pool_id):
        pool_range_tuple_list = Pool.get_range_as_tuple_list(pool_id)
        existing_range_numbers_list = PoolLease.get_pool_lease_range_numbers(pool_id)

        for pool_range in pool_range_tuple_list:
            for range_number in range(pool_range[0], pool_range[1]+1):
                range_number_count = existing_range_numbers_list.count(range_number)
                if range_number_count == 0:
                    return range_number
        
        return None