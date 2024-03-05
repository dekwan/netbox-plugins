from netbox.filtersets import NetBoxModelFilterSet
from utilities.forms.fields import DynamicModelChoiceField

from .models import Pool, PoolLease


class PoolFilterSet(NetBoxModelFilterSet):

    class Meta:
        model = Pool
        fields = ('id', 'name', 'description', 'range')

    def search(self, queryset, name, value):
        return queryset.filter(name__icontains=value) | queryset.filter(description__icontains=value) | queryset.filter(range__icontains=value)


class PoolLeaseFilterSet(NetBoxModelFilterSet):

    class Meta:
        model = PoolLease
        fields = ('id', 'pool', 'requester_id', 'requester_details')

    def search(self, queryset, name, value):
        return queryset.filter(pool__name__icontains=value) | queryset.filter(requester_id__icontains=value) | queryset.filter(requester_details__icontains=value)