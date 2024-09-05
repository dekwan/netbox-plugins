import json

from django.db.models import Count
from netbox.api.viewsets import NetBoxModelViewSet
from rest_framework import status
from rest_framework.response import Response

from .. import filtersets, models
from ..utilities import fetchDataByName
from .serializers import DeviceInfoAPISerializer


class DeviceInfoViewSet(NetBoxModelViewSet):
    queryset = models.DeviceInfo.objects.all()
    serializer_class = DeviceInfoAPISerializer
    filterset_class = filtersets.DeviceInfoFilterSet

    def post(self, request):
        # Get the request body
        request_body = request.body.decode("utf-8")
        if not request_body:
            return Response([{"error": "Missing request body."}], status=status.HTTP_400_BAD_REQUEST)
        data = json.loads(request_body)

        # Get the values from the request body
        site_name = data.get("site_name")
        device_name = data.get("device_name")
        device_setup_type = data.get("device_setup_type")
        remote_config = data.get("remote_config")

        if not(site_name and device_name and device_setup_type):
            return Response([{"error": "Missing one or more of the required parameters (site_name, device_name, and/or device_setup_type)."}], status=status.HTTP_400_BAD_REQUEST)

        return fetchDataByName(site_name, device_name, device_setup_type, remote_config)
