from netbox.api.routers import NetBoxRouter
from . import views


app_name = 'pool_manager'

router = NetBoxRouter()
router.register('pool', views.PoolViewSet)
router.register('poollease', views.PoolLeaseViewSet)

urlpatterns = router.urls