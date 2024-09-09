import django_filters
from netbox.filtersets import NetBoxModelFilterSet
from utilities.filters import MultiValueCharFilter

from .models import DeviceInfo, VlanInfo


class DeviceInfoFilterSet(NetBoxModelFilterSet):

    site = MultiValueCharFilter(
        lookup_expr='icontains'
    )
    device = MultiValueCharFilter(
        lookup_expr='icontains'
    )
    device_setup_type = MultiValueCharFilter(
        lookup_expr='icontains'
    )
    remote_config = MultiValueCharFilter(
        lookup_expr='icontains'
    )

    class Meta:
        model = DeviceInfo
        fields = ('id', 'site', 'device', 'device_setup_type', 'remote_config')


class VlanInfoFilterSet(NetBoxModelFilterSet):

    site = MultiValueCharFilter(
        lookup_expr='icontains'
    )
    vlan = MultiValueCharFilter(
        lookup_expr='icontains'
    )

    class Meta:
        model = VlanInfo
        fields = ('id', 'site', 'vlan')