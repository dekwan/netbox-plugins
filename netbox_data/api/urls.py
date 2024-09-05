from netbox.api.routers import NetBoxRouter

from . import views

app_name = 'netbox_data'

router = NetBoxRouter()
router.register('deviceInfo', views.DeviceInfoViewSet)

urlpatterns = router.urls