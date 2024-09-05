from netbox.search import SearchIndex, register_search

from .models import DeviceInfo


@register_search
class DeviceInfoIndex(SearchIndex):
    model = DeviceInfo
    fields = (
        ('site', 100),
        ('device', 5000),
        ('device_setup_type', 5000),
        ('remote_config', 5000)
    )