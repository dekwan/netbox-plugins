import django_tables2 as tables
from netbox.tables import NetBoxTable

from .models import DeviceInfo


class DeviceInfoTable(NetBoxTable):
    id = tables.Column(
        linkify=True
    )

    class Meta(NetBoxTable.Meta):
        model = DeviceInfo
        fields = ('pk', 'id', 'site', 'device', 'device_setup_type', 'remote_config', 'actions')
        default_columns = ('id', 'site', 'device', 'device_setup_type', 'remote_config')