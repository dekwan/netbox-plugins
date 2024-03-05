from netbox.api.serializers import NetBoxModelSerializer
from dcim.models import Site

class NetboxDataSerializer(NetBoxModelSerializer):

    class Meta:
        model = Site
        fields = ()