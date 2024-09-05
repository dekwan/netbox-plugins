from netbox.plugins import PluginConfig

class NetboxDataConfig(PluginConfig):
    name = 'netbox_data'
    verbose_name = 'Netbox Data'
    description = 'Get netbox data'
    version = '0.1'
    base_url = 'netbox-data'
    min_version = '3.4.0'

config = NetboxDataConfig
