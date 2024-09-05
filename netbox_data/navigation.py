from netbox.plugins import PluginMenuButton, PluginMenuItem


data_buttons = [
    PluginMenuButton(
        link='plugins:netbox_data:deviceinfo_add',
        title='Run',
        icon_class='mdi mdi-plus-thick'
    )
]

menu_items = (
    PluginMenuItem(
        link='plugins:netbox_data:deviceinfo_list',
        link_text='Device Info',
        buttons=data_buttons
    ),
)
