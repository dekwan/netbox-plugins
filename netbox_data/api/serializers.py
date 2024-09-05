from multiprocessing import pool

from dcim.models import Device, Site
from django.http import Http404, HttpResponse, HttpResponseBadRequest
from netbox.api.serializers import (NetBoxModelSerializer,
                                    WritableNestedSerializer)
from rest_framework import serializers

from ..models import DeviceInfo
from ..utilities import fetch_data

#
# Nested serializers
#

class NestedDeviceInfoSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='plugins-api:netbox_data-api:deviceinfo-detail',
    )

    class Meta:
        model = DeviceInfo
        fields = ('id', 'url', 'display', 'site', 'device', 'device_setup_type', 'remote_config', 'results')

class DeviceInfoSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='plugins-api:netbox_data-api:deviceinfo-detail'
    )

    class Meta:
        model = DeviceInfo
        fields = ('id', 'url', 'site', 'device', 'device_setup_type', 'remote_config', 'results',
            'created', 'last_updated',)
    
    def __init__(self, *args, **kwargs):
        kwargs['partial'] = True
        super(DeviceInfoSerializer, self).__init__(*args, **kwargs)

class DeviceInfoAPISerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='plugins-api:netbox_data-api:deviceinfo-detail'
    )
    site_name = serializers.CharField(write_only=True)
    device_name = serializers.CharField(write_only=True)

    class Meta:
        model = DeviceInfo
        fields = ('id', 'url', 'site_name', 'device_name', 'device_setup_type', 'remote_config', 'results',
            'created', 'last_updated',)
    
    def __init__(self, *args, **kwargs):
        kwargs['partial'] = True
        super(DeviceInfoAPISerializer, self).__init__(*args, **kwargs)

    def create(self, validated_data):
        site = validated_data['site']
        device = site = validated_data['device']
        response = fetch_data(site.id, device.id, validated_data['device_setup_type'], '')
        validated_data['results'] = response.data
        return super().create(validated_data)

    def validate(self, data):
        site = Site.objects.get(name=data['site_name']) # Throws a Site.DoesNotExist if it does not exist
        device_info = Device.objects.get(name=data['device_name'], site=site.id)
        
        data['site'] = site
        data['device'] = device_info
        data.pop('site_name', None)
        data.pop('device_name', None)

        return super().validate(data)