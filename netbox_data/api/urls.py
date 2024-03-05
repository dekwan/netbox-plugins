from django.urls import path
from netbox.api.routers import NetBoxRouter
from .views import NetboxDataDeviceViewSet
from .views import NetboxDataVlanViewSet

app_name = 'netbox_data'
router = NetBoxRouter()

urlpatterns = [
    path('device/', NetboxDataDeviceViewSet.as_view(), name='device'),
    path('vlan/', NetboxDataVlanViewSet.as_view(), name='vlan')
]

urlpatterns += router.urls