from django.urls import path
from netbox.api.routers import NetBoxRouter

from . import views

app_name = 'netbox_data'

router = NetBoxRouter()

urlpatterns = [
    path('device/', views.DeviceInfoViewSet.as_view(), name='device'),
    path('vlan/', views.VlanInfoViewSet.as_view(), name='vlan')
]

urlpatterns += router.urls