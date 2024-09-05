from dcim.models import Device, Site
from django.db import models
from django.urls import reverse
from netbox.models import NetBoxModel


class DeviceSetupTypeChoices(models.TextChoices):
    CLEAN = u'clean', 'Clean'
    RESERVATION = u'reservation', 'Reservation'

class DeviceInfo(NetBoxModel):
    site = models.ForeignKey(
        to=Site,
        on_delete=models.PROTECT,
        blank=False
    )
    device = models.ForeignKey(
        to=Device,
        on_delete=models.PROTECT,
        blank=False
    )
    device_setup_type = models.CharField(
        max_length=100,
        blank=False,
        choices=DeviceSetupTypeChoices.choices,
        default=DeviceSetupTypeChoices.CLEAN,
        help_text="Clean or reservation."
    )
    remote_config = models.CharField(
        max_length=100,
        unique=False,
        blank=True,
        help_text="The config file to be downloaded from the fileserver."
    )
    results = models.JSONField(
        blank=True,
        default=dict,
        help_text="The response of the request."
    )

    class Meta:
        ordering = ('site',)

    def __str__(self):
        return f'site: {self.site}, device: {self.device}, device_setup_type: {self.device_setup_type}, remote_config: {self.remote_config}'

    def get_absolute_url(self):
        return reverse('plugins:netbox_data:deviceInfo', args=[self.pk])