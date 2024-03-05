from extras.plugins import PluginMenuButton, PluginMenuItem
from utilities.choices import ButtonColorChoices

pool_buttons = [
    PluginMenuButton(
        link='plugins:pool_manager:pool_add',
        title='Add',
        icon_class='mdi mdi-plus-thick',
        color=ButtonColorChoices.GREEN
    )
]

poollease_butons = [
    PluginMenuButton(
        link='plugins:pool_manager:poollease_add',
        title='Add',
        icon_class='mdi mdi-plus-thick',
        color=ButtonColorChoices.GREEN
    )
]

menu_items = (
    PluginMenuItem(
        link='plugins:pool_manager:pool_list',
        link_text='Pool',
        buttons=pool_buttons
    ),
    PluginMenuItem(
        link='plugins:pool_manager:poollease_list',
        link_text='Pool Lease',
        buttons=poollease_butons
    ),
)
