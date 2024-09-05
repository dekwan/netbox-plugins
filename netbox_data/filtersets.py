import django_filters
from netbox.filtersets import NetBoxModelFilterSet
from utilities.filters import MultiValueCharFilter

from .models import DeviceInfo


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