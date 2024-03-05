from django.db.models import Count

from netbox.api.viewsets import NetBoxModelViewSet

from .. import filtersets, models
from .serializers import PoolSerializer, PoolLeaseSerializer


class PoolViewSet(NetBoxModelViewSet):
    queryset = models.Pool.objects.annotate(
        lease_count=Count('lease_to_pool')
    )
    serializer_class = PoolSerializer

class PoolLeaseViewSet(NetBoxModelViewSet):
    queryset = models.PoolLease.objects.prefetch_related(
        'pool'
    )
    serializer_class = PoolLeaseSerializer
    filterset_class = filtersets.PoolLeaseFilterSet