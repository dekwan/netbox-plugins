from graphene import ObjectType
from netbox.graphql.types import NetBoxObjectType
from netbox.graphql.fields import ObjectField, ObjectListField
from . import filtersets, models


#
# Object types
#

class PoolType(NetBoxObjectType):

    class Meta:
        model = models.Pool
        fields = '__all__'


class PoolLeaseType(NetBoxObjectType):

    class Meta:
        model = models.PoolLease
        fields = '__all__'
        filterset_class = filtersets.PoolLeaseFilterSet

#
# Queries
#

class Query(ObjectType):
    pool = ObjectField(PoolType)
    pool_list = ObjectListField(PoolType)

    pool_lease = ObjectField(PoolLeaseType)
    pool_lease_list = ObjectListField(PoolLeaseType)


schema = Query
