from multiprocessing import pool
from rest_framework import serializers

from netbox.api.serializers import NetBoxModelSerializer, WritableNestedSerializer
from ..models import Pool, PoolLease

from django.http import HttpResponseBadRequest, HttpResponse, Http404


#
# Nested serializers
#

class NestedPoolSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='plugins-api:pool_manager-api:pool-detail',
    )

    class Meta:
        model = Pool
        fields = ('id', 'url', 'display', 'name', 'description', 'range')


class PoolSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='plugins-api:pool_manager-api:pool-detail'
    )
    lease_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Pool
        fields = ('id', 'url', 'name', 'description', 'range', 'lease_count', 'created',
            'last_updated',)
    
    def __init__(self, *args, **kwargs):
        kwargs['partial'] = True
        super(PoolSerializer, self).__init__(*args, **kwargs)

    def validate(self, data):
        try:
            if self.instance and 'range' in data: # It is a PUT
                pool = Pool.get_pool_by_id(self.instance.id)

                # If the range changed
                if pool.range != data['range']:
                    if len(PoolLease.get_pool_lease_range_numbers(pool.id)) > 0:
                        # Error occured
                        raise serializers.ValidationError({
                            'range': 'Cannot change the range for this pool because there are existing leases.'
                        })
        except (PoolLease.DoesNotExist, Pool.DoesNotExist, KeyError):
            # The pool doesn't exist yet so do nothing
            pass

        return super(PoolSerializer, self).validate(data)
        


class PoolLeaseSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='plugins-api:pool_manager-api:poollease-detail'
    )
    pool = NestedPoolSerializer()
    range_number = serializers.IntegerField(required=False, default=0)

    class Meta:
        model = PoolLease
        fields = (
            'id', 'url', 'display', 'pool', 'requester_id', 'requester_details',
            'range_number', 'created', 'last_updated',
        )
        validators = []

    def __init__(self, *args, **kwargs):
        kwargs['partial'] = True
        super(PoolLeaseSerializer, self).__init__(*args, **kwargs)
    
    def validate(self, data):
        if 'pool' in data:
            pool_id = data['pool'].id
            if self.instance: # It is a PUT and pool is changing
                pool_lease = PoolLease.get_pool_lease(self.instance.id)

                # If the pool didn't change
                if pool_lease.pool.id == pool_id:
                    # Do nothing
                    return super(PoolLeaseSerializer, self).validate(data)

            range_number = PoolLease.get_lease_range_number(pool_id)
            if range_number == None:
                raise serializers.ValidationError({
                    'pool': 'There are no leases available for this pool.'
                })
            else: 
                data['range_number'] = range_number
        
        return super(PoolLeaseSerializer, self).validate(data)