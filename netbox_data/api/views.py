import json

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .. import filtersets, models
from ..utilities import fetchDeviceInfoByName, fetchVlanInfoByNameVid
from .serializers import DeviceInfoAPISerializer, VlanInfoAPISerializer

FIELD_MISSING = "This field cannot be blank."

class DeviceInfoViewSet(APIView):
    queryset = models.DeviceInfo.objects.all()
    serializer_class = DeviceInfoAPISerializer
    filterset_class = filtersets.DeviceInfoFilterSet

    def get(self, request):
        # Get the request body
        request_body = request.body.decode("utf-8")
        if not request_body:
            return Response({"error": "Missing request body."}, status=status.HTTP_400_BAD_REQUEST)
        data = json.loads(request_body)

        # Get the values from the request body
        site_name = data.get("site_name")
        device_name = data.get("device_name")
        device_setup_type = data.get("device_setup_type")
        remote_config = data.get("remote_config")

        response_text = {}
        if not site_name:
            response_text['site_name'] = [f'{FIELD_MISSING}']
        if not device_name:
            response_text['device_name'] = [f'{FIELD_MISSING}']
        if not device_setup_type:
            response_text['device_setup_type'] = [f'{FIELD_MISSING}']

        if response_text != {}:
            return Response(response_text, status=status.HTTP_400_BAD_REQUEST)
        
        return fetchDeviceInfoByName(site_name, device_name, device_setup_type, remote_config)


class VlanInfoViewSet(APIView):
    queryset = models.VlanInfo.objects.all()
    serializer_class = VlanInfoAPISerializer
    filterset_class = filtersets.VlanInfoFilterSet

    def get(self, request):
        # Get the request body
        request_body = request.body.decode("utf-8")
        if not request_body:
            return Response({"error": "Missing request body."}, status=status.HTTP_400_BAD_REQUEST)
        data = json.loads(request_body)

        # Get the values from the request body
        site_name = data.get("site_name")
        vlan = data.get("vlan")

        response_text = {}
        if not site_name:
            response_text['site_name'] = [f'{FIELD_MISSING}']
        if not vlan:
            response_text['vlan'] = [f'{FIELD_MISSING}']

        if response_text != {}:
            return Response(response_text, status=status.HTTP_400_BAD_REQUEST)

        return fetchVlanInfoByNameVid(site_name, vlan)
