from netbox.plugins import PluginMenuButton, PluginMenuItem


deviceInfo_buttons = [
    PluginMenuButton(
        link='plugins:netbox_data:deviceinfo_add',
        title='Run',
        icon_class='mdi mdi-plus-thick'
    )
]

vlanInfo_buttons = [
    PluginMenuButton(
        link='plugins:netbox_data:vlaninfo_add',
        title='Run',
        icon_class='mdi mdi-plus-thick'
    )
]


menu_items = (
    PluginMenuItem(
        link='plugins:netbox_data:deviceinfo_list',
        link_text='Device',
        buttons=deviceInfo_buttons
    ),
    PluginMenuItem(
        link='plugins:netbox_data:vlaninfo_list',
        link_text='Vlan',
        buttons=vlanInfo_buttons
    ),
)