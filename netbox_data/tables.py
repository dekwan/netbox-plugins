import django_tables2 as tables
from netbox.tables import NetBoxTable

from .models import DeviceInfo, VlanInfo


class DeviceInfoTable(NetBoxTable):
    id = tables.Column(
        linkify=True
    )

    class Meta(NetBoxTable.Meta):
        model = DeviceInfo
        fields = ('pk', 'id', 'site', 'device', 'device_setup_type', 'remote_config', 'actions')
        default_columns = ('id', 'site', 'device', 'device_setup_type', 'remote_config')


class VlanInfoTable(NetBoxTable):
    id = tables.Column(
        linkify=True
    )

    class Meta(NetBoxTable.Meta):
        model = VlanInfo
        fields = ('pk', 'id', 'site', 'vlan' 'actions')
        default_columns = ('id', 'site', 'vlan')