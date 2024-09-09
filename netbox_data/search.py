from netbox.search import SearchIndex, register_search

from .models import DeviceInfo, VlanInfo


@register_search
class DeviceInfoIndex(SearchIndex):
    model = DeviceInfo
    fields = (
        ('site', 100),
        ('device', 5000),
        ('device_setup_type', 5000),
        ('remote_config', 5000)
    )


@register_search
class VlanInfoIndex(SearchIndex):
    model = VlanInfo
    fields = (
        ('site', 100),
        ('vlan', 5000)
    )