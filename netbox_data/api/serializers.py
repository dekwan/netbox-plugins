
from dcim.models import Device, Site
from django.core.exceptions import ValidationError
from ipam.models import VLAN
from netbox.api.serializers import NetBoxModelSerializer
from rest_framework import serializers

from ..models import DeviceInfo, VlanInfo
from ..utilities import fetchDeviceInfo, fetchVlanInfo


# Serializer for the UI
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

# Serializer for the API
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
        device = validated_data['device']
        response = fetchDeviceInfo(site.id, device.id, validated_data['device_setup_type'], '')
        validated_data['results'] = response.data
        return super().create(validated_data)

    def validate(self, data):
        try:
            site = Site.objects.get(name=data['site_name'])
            device_info = Device.objects.get(name=data['device_name'], site=site.id)
            
            data['site'] = site
            data['device'] = device_info
            data.pop('site_name', None)
            data.pop('device_name', None)
        except Site.DoesNotExist:
            raise ValidationError({"site_name": f"Site {data['site_name']} does not exist."})
        except Device.DoesNotExist:
            raise ValidationError({"site_name": f"Device {data['device_name']} does not exist."})
        except Exception as e:
            raise ValidationError({"error": f"An error occurred: {e}."})

        return super().validate(data)

# Serializer for the UI
class VlanInfoSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='plugins-api:netbox_data-api:vlaninfo-detail'
    )

    class Meta:
        model = VlanInfo
        fields = ('id', 'url', 'site', 'vlan', 'results', 'created', 'last_updated',)
    
    def __init__(self, *args, **kwargs):
        kwargs['partial'] = True
        super(VlanInfoSerializer, self).__init__(*args, **kwargs)

# Serializer for the API
class VlanInfoAPISerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='plugins-api:netbox_data-api:vlaninfo-detail'
    )
    site_name = serializers.CharField(write_only=True)
    vlan_vid = serializers.CharField(write_only=True)

    class Meta:
        model = VlanInfo
        fields = ('id', 'url', 'site_name', 'vlan_vid', 'results', 'created', 'last_updated',)
    
    def __init__(self, *args, **kwargs):
        kwargs['partial'] = True
        super(VlanInfoAPISerializer, self).__init__(*args, **kwargs)

    def create(self, validated_data):
        site = validated_data['site']
        vlan = validated_data['vlan']
        response = fetchVlanInfo(site.id, vlan.id)
        validated_data['results'] = response.data
        return super().create(validated_data)

    def validate(self, data):
        try:
            site = Site.objects.get(name=data['site_name']) # TODO: Throws a Site.DoesNotExist if it does not exist
            vlan = VLAN.objects.get(vid=data['vlan_vid'], site=site.id)
            
            data['site'] = site
            data['vlan'] = vlan
            data.pop('site_name', None)
            data.pop('vlan_vid', None)
        except Site.DoesNotExist:
            raise ValidationError({"site_name": f"Site {data['site_name']} does not exist."})
        except VLAN.DoesNotExist:
            raise ValidationError({"site_name": f"VLAN {data['vlan_vid']} with site {data['site_name']} does not exist."})
        except Exception as e:
            raise ValidationError({"error": f"An error occurred: {e}."})
        
        return super().validate(data)