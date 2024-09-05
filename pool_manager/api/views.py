from django.db.models import Count
from netbox.api.viewsets import NetBoxModelViewSet
from rest_framework import status
from rest_framework.response import Response

from .. import filtersets, models
from .serializers import PoolLeaseSerializer, PoolSerializer


class PoolViewSet(NetBoxModelViewSet):
    queryset = models.Pool.objects.annotate(
        lease_count=Count('lease_to_pool')
    )
    serializer_class = PoolSerializer
    filterset_class = filtersets.PoolFilterSet

class PoolLeaseViewSet(NetBoxModelViewSet):
    queryset = models.PoolLease.objects.prefetch_related(
        'pool'
    )
    serializer_class = PoolLeaseSerializer
    filterset_class = filtersets.PoolLeaseFilterSet

    def create(self, request, *args, **kwargs):
        
        # Get the request count from the request body
        request_count = 1
        if request.data.get('request_count'):
            try:
                request_count = int(request.data['request_count'])
            except:
                pass

        # Make sure there are enough available leases in the pool
        pool = models.Pool.get_pool_by_id(request.data['pool'])
        pool_size, in_use, available = pool.get_pool_lease_details()

        if available < request_count:
            return Response({'error': 'There are not enough pool leases available in the pool.'}, status=status.HTTP_400_BAD_REQUEST)

        response_body = []
        for i in range(request_count):
            response_instance = super().create(request, *args, **kwargs)
            if response_instance.status_code == 201:
                response_body.append(response_instance.data)
            else:
                return Response({'error': 'There was an error creating the pool leases.'}, status=status.HTTP_400_BAD_REQUEST)

        return Response(response_body, status=status.HTTP_201_CREATED)
    
    def bulk_destroy(self, request, *args, **kwargs):
        if isinstance(request.data, dict):
            qs = super().get_bulk_destroy_queryset()
            if 'tag' in request.data:
                qs = qs.filter(tag=request.data['tag'])
                super().perform_bulk_destroy(qs)

                return Response(status=status.HTTP_204_NO_CONTENT)
            if 'requester_id' in request.data:
                qs = qs.filter(requester_id=request.data['requester_id'])
                super().perform_bulk_destroy(qs)

                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                return Response({'error': 'Missing tag field'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return super().bulk_destroy(request, *args, **kwargs)