from django import forms
from django.forms import ModelForm
from netbox.forms import NetBoxModelFilterSetForm
from utilities.forms.fields import DynamicModelChoiceField

from .models import AlgorithmChoices, Pool, PoolLease


class PoolForm(ModelForm):
    class Meta:
        model = Pool
        fields = ('name', 'description', 'range', 'algorithm')

    def clean(self):
        if 'range' in self.changed_data:
            new_range = self.data['range']
            range_as_list = Pool.get_range_as_list(new_range)

            if range_as_list == None:
                    # Invalid range
                    self.add_error('range', f'Enter a valid range.')
            else:
                try:
                    pool = Pool.get_pool_by_name(self.data['name'])

                    
                    existing_pool_leases = PoolLease.get_pool_lease_range_numbers(pool)
                    reset_index = True
                    for pool_lease in existing_pool_leases:
                        if pool_lease not in range_as_list:
                            # Error occured
                            self.add_error('range', f'Cannot change the range for this pool. Please remove pool lease {pool_lease} first.')
                            reset_index = False
                    
                    if reset_index:
                        self.instance.index = 0
                except (PoolLease.DoesNotExist, Pool.DoesNotExist, KeyError):
                    # New pool so do nothing.
                    pass
        
        return super().clean()


class PoolFilterForm(NetBoxModelFilterSetForm):
    model = Pool
    name = forms.CharField(
        required=False
    )
    description = forms.CharField(
        required=False
    )
    algorithm = forms.MultipleChoiceField(
        required=False,
        choices=AlgorithmChoices
    )

class PoolLeaseAddForm(ModelForm):
    request_count = forms.IntegerField(
        required=False,
        initial=1,
        help_text='The number of leases requested.'
    )

    class Meta:
        model = PoolLease
        fields = ('pool', 'requester_id', 'requester_details', 'request_count', 'range_number', 'tag')
        exclude = ('range_number',)

    def clean(self):

        request_count = 1
        if self.data['request_count']:
            request_count = int(self.data['request_count'])

        pool_id = int(self.data['pool'])
        pool = Pool.get_pool_by_id(pool_id)
        pool_size, in_use, available = pool.get_pool_lease_details()

        if request_count > available:
            self.add_error('request_count', f'There are not enough leases available for this request.')

        return super().clean()

    def save(self, *args, **kwargs):
        request_count = 1
        if self.data['request_count']:
            request_count = int(self.data['request_count'])

        # Do not need to check to that there are enough leases available
        # because it was already done in clean()
        for i in range(request_count):
            form = PoolLeaseForm(data=self.data)
            instance = form.save()

        return instance


class PoolLeaseForm(ModelForm):
    pool = DynamicModelChoiceField(
        queryset=Pool.objects.all()
    )

    class Meta:
        model = PoolLease
        fields = ('pool', 'requester_id', 'requester_details', 'range_number', 'tag')
        exclude = ('range_number',)

    def clean(self):
        # Pool changed so assign a lease
        if 'pool' in self.changed_data:
            pool_id = int(self.data['pool'])

            # Assign the lease a pool range number
            lease_range_number = self.Meta.model.get_lease_range_number(pool_id)
            if lease_range_number == None:
                # Error occured
                self.add_error('pool', f'There are no leases available for this pool.')
            else:
                self.instance.range_number = lease_range_number

        return super().clean()


class PoolLeaseFilterForm(NetBoxModelFilterSetForm):
    model = PoolLease
    pool = forms.ModelMultipleChoiceField(
        queryset=Pool.objects.all(),
        required=False
    )
    requester_id = forms.CharField(
        required=False
    )
    requester_details = forms.CharField(
        required=False
    )
    tag = forms.CharField(
        required=False
    )