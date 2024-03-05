from netbox.search import SearchIndex, register_search
from .models import Pool, PoolLease


@register_search
class PoolIndex(SearchIndex):
    model = Pool
    fields = (
        ('name', 100),
        ('description', 5000),
        ('range', 5000)
    )


@register_search
class PoolLeaseIndex(SearchIndex):
    model = PoolLease
    fields = (
        ('pool', 100),
        ('requester_id', 100),
        ('requester_details', 100)
    )