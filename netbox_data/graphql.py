from graphene import ObjectType
from netbox.graphql.fields import ObjectField, ObjectListField
from netbox.graphql.types import NetBoxObjectType

from . import models

#
# Object types
#

class DeviceInfoType(NetBoxObjectType):

    class Meta:
        model = models.DeviceInfo
        fields = '__all__'

#
# Queries
#

class Query(ObjectType):
    deviceinfo = ObjectField(DeviceInfoType)
    deviceinfo_list = ObjectListField(DeviceInfoType)

schema = Query
