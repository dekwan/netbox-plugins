from django.urls import path
from netbox.api.routers import NetBoxRouter

from . import views

app_name = 'netbox_data'

router = NetBoxRouter()

# URLs for the UI
router.register('deviceInfo', views.DeviceInfoViewSet)
router.register('vlanInfo', views.VlanInfoViewSet)

# URLs for the API
urlpatterns = [
    path('device/', views.DeviceInfoAPIViewSet.as_view(), name='device'),
    path('vlan/', views.VlanInfoAPIViewSet.as_view(), name='vlan')
]

urlpatterns += router.urls