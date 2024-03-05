from django import forms

from netbox.forms import NetBoxModelForm, NetBoxModelFilterSetForm
from utilities.forms.fields import DynamicModelChoiceField
from .models import Pool, PoolLease


class PoolForm(NetBoxModelForm):
    class Meta:
        model = Pool
        fields = ('name', 'description', 'range')

    def clean(self):
        if 'range' in self.changed_data:
            try:
                pool_id = Pool.get_pool_by_name(self.data['name'])
                if len(PoolLease.get_pool_lease_range_numbers(pool_id)) > 0:
                    # Error occured
                    self.add_error('range', f'Cannot change the range for this pool because there are existing leases.')
            except Pool.DoesNotExist:
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
    range = forms.CharField(
        required=False
    )


class PoolLeaseForm(NetBoxModelForm):
    pool = DynamicModelChoiceField(
        queryset=Pool.objects.all()
    )

    class Meta:
        model = PoolLease
        fields = ('pool', 'requester_id', 'requester_details', 'range_number')
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