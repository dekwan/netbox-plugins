from dcim.models import Device, Site
from django import forms
from django.forms import ModelForm
from netbox.forms import NetBoxModelFilterSetForm, NetBoxModelForm

from .models import DeviceInfo
from .utilities import fetch_data


class DeviceInfoForm(ModelForm):
    class Meta:
        model = DeviceInfo
        fields = ('site', 'device', 'device_setup_type', 'remote_config')

    def clean(self):
        # Get the values from the request body
        site_id = self.data['site']
        device_id = self.data['device']
        device_setup_type = self.data['device_setup_type']
        remote_config = self.data['remote_config']

        site = Site.objects.get(id=site_id) # Throws a Site.DoesNotExist if it does not exist
        device = Device.objects.get(id=device_id, site=site_id)

        response = fetch_data(site_id, device_id, device_setup_type, remote_config)

        self.instance.site_name = site.name
        self.instance.device_name = device.name
        self.instance.data = response.data
        
        return super().clean()


class DeviceInfoFilterForm(NetBoxModelFilterSetForm):
    model = DeviceInfo
    site = forms.CharField(
        required=False
    )
    device = forms.CharField(
        required=False
    )
    device_setup_type = forms.CharField(
        required=False
    )
    remote_config = forms.CharField(
        required=False
    )
    results = forms.JSONField(
        required=False
    )