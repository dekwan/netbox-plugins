
from netbox.api.serializers import (NetBoxModelSerializer,
                                    WritableNestedSerializer)
from rest_framework import serializers

from ..models import Pool, PoolLease

#
# Nested serializers
#

class NestedPoolSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='plugins-api:pool_manager-api:pool-detail',
    )

    class Meta:
        model = Pool
        fields = ('id', 'url', 'display', 'name', 'description', 'range', 'algorithm')


class PoolSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='plugins-api:pool_manager-api:pool-detail'
    )
    lease_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Pool
        fields = ('id', 'url', 'name', 'description', 'range', 'algorithm', 'lease_count',
            'created', 'last_updated',)
    
    def __init__(self, *args, **kwargs):
        kwargs['partial'] = True
        super(PoolSerializer, self).__init__(*args, **kwargs)

    def validate(self, data):
        # Validate the range
        if 'range' in data:
            new_range = data['range']
            range_as_list = Pool.get_range_as_list(new_range)
            if range_as_list == None:
                raise serializers.ValidationError({
                        'range': f'Enter a valid range.'
                    })
            
            # Check to see if the range can be changed
            try:
                if self.instance: # It is a PUT
                    pool = Pool.get_pool_by_id(self.instance.id)

                    # If the range changed
                    if pool.range != new_range:
                        existing_pool_leases = PoolLease.get_pool_lease_range_numbers(pool)
                        for pool_lease in existing_pool_leases:
                            if pool_lease not in range_as_list:
                                # Error occured
                                raise serializers.ValidationError({
                                    'range': f'Cannot change the range for this pool. Please remove pool lease {pool_lease} first.'
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
    range_number = serializers.CharField(required=False)
    tag = serializers.CharField(required=False)

    class Meta:
        model = PoolLease
        fields = (
            'id', 'url', 'display', 'pool', 'requester_id', 'requester_details',
            'range_number', 'tag', 'created', 'last_updated',
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
            
            # If a specific range number is requested
            if 'range_number' in data:
                existing_range_numbers_list = self.Meta.model.get_pool_lease_range_numbers(pool_id)

                requested_range_number = data['range_number']
                if requested_range_number in existing_range_numbers_list:
                    # Requested range number is already in use
                    raise serializers.ValidationError({
                        'range_number': 'The requested range number is already in use.'
                    })
                else:
                    data['range_number'] = requested_range_number
            else:
                # Pool changed so assign the lease a pool range number
                lease_range_number = self.Meta.model.get_lease_range_number(pool_id)
                if lease_range_number == None:
                    # Error occured
                    raise serializers.ValidationError({
                        'pool': 'There are no leases available for this pool.'
                    })
                else:
                    data['range_number'] = lease_range_number
        
        return super(PoolLeaseSerializer, self).validate(data)