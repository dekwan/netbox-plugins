from netbox.plugins import PluginConfig

class NetboxDataConfig(PluginConfig):
    name = 'pool_manager'
    verbose_name = 'Pool Manager'
    description = 'Simple pool manager'
    version = '0.1'
    base_url = 'pool-manager'
    min_version = '3.4.0'

config = NetboxDataConfig
