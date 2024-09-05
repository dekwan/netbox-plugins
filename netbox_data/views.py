from netbox.views import generic

from . import filtersets, forms, models, tables

#
# DeviceInfo views
#

class DeviceInfoView(generic.ObjectView):
    queryset = models.DeviceInfo.objects.all()


class DeviceInfoListView(generic.ObjectListView):
    queryset = models.DeviceInfo.objects.all()
    table = tables.DeviceInfoTable
    filterset = filtersets.DeviceInfoFilterSet
    filterset_form = forms.DeviceInfoFilterForm


class DeviceInfoEditView(generic.ObjectEditView):
    queryset = models.DeviceInfo.objects.all()
    form = forms.DeviceInfoForm


class DeviceInfoDeleteView(generic.ObjectDeleteView):
    queryset = models.DeviceInfo.objects.all()


class DeviceInfoBulkDeleteView(generic.BulkDeleteView):
    queryset = models.DeviceInfo.objects.all()
    filterset = filtersets.DeviceInfoFilterSet
    table = tables.DeviceInfoTable