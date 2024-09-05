import django_filters
from netbox.filtersets import NetBoxModelFilterSet
from utilities.filters import MultiValueCharFilter

from .models import AlgorithmChoices, Pool, PoolLease


class PoolFilterSet(NetBoxModelFilterSet):

    name = MultiValueCharFilter(
        lookup_expr='icontains'
    )
    description = MultiValueCharFilter(
        lookup_expr='icontains'
    )
    algorithm = django_filters.MultipleChoiceFilter(
        choices=AlgorithmChoices,
        null_value=None
    )

    class Meta:
        model = Pool
        fields = ('id', 'name', 'description', 'algorithm')
        


class PoolLeaseFilterSet(NetBoxModelFilterSet):
    pool = django_filters.ModelMultipleChoiceFilter(
        queryset=Pool.objects.all(),
    )
    requester_id = MultiValueCharFilter(
        lookup_expr='icontains'
    )
    requester_details = MultiValueCharFilter(
        lookup_expr='icontains'
    )
    tag = MultiValueCharFilter(
        lookup_expr='icontains'
    )

    class Meta:
        model = PoolLease
        fields = ('id', 'pool', 'requester_id', 'requester_details', 'tag')