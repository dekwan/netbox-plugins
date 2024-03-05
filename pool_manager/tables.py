import django_tables2 as tables

from netbox.tables import NetBoxTable
from .models import Pool, PoolLease


class PoolTable(NetBoxTable):
    name = tables.Column(
        linkify=True
    )
    lease_count = tables.Column()

    class Meta(NetBoxTable.Meta):
        model = Pool
        fields = ('pk', 'id', 'name', 'description', 'range', 'lease_count', 'actions')
        default_columns = ('name', 'description', 'range', 'lease_count')


class PoolLeaseTable(NetBoxTable):
    requester_id = tables.Column(
        linkify=True
    )

    class Meta(NetBoxTable.Meta):
        model = PoolLease
        fields = ('pk', 'id', 'requester_id', 'requester_details', 'pool', 'range_number', 'actions')
        default_columns = ('requester_id', 'requester_details', 'pool', 'range_number')
