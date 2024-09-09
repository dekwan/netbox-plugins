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

        if 'pool' not in request.data:
            return Response({'pool': ["This field cannot be blank."]}, status=status.HTTP_400_BAD_REQUEST)
        
        # Get the request count from the request body
        request_count = 1
        if 'request_count' in request.data and request.data.get('request_count'):
            try:
                request_count = int(request.data['request_count'])
            except:
                pass

        # Make sure there are enough available leases in the pool
        try:
            pool = models.Pool.get_pool_by_id(request.data['pool'])
            pool_size, in_use, available = pool.get_pool_lease_details()

            if available < request_count:
                return Response({'request_count': ["There are not enough pool leases available in the pool."]}, status=status.HTTP_400_BAD_REQUEST)

            response_body = []
            for i in range(request_count):
                response_instance = super().create(request, *args, **kwargs)
                if response_instance.status_code == 201:
                    response_body.append(response_instance.data)
                else:
                    return Response({'error': 'There was an error creating the pool leases.'}, status=status.HTTP_400_BAD_REQUEST)
        except models.Pool.DoesNotExist:
            return Response({'pool': [f"Pool {request.data['pool']} does not exist."]}, status=status.HTTP_400_BAD_REQUEST)
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
            
            return Response({'tag': ["This field or requester_id cannot be blank."], 'requester_id': ["This field or tag cannot be blank."]}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return super().bulk_destroy(request, *args, **kwargs)