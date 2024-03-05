from extras.plugins import PluginConfig

class PoolManagerConfig(PluginConfig):
    name = 'pool_manager'
    verbose_name = 'Pool Manager'
    description = 'Simple pool manager'
    version = '0.1'
    base_url = 'pool-manager'
    min_version = '3.4.0'

config = PoolManagerConfig
