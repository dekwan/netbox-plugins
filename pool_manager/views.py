from django.db.models import Count

from netbox.views import generic
from . import filtersets, forms, models, tables


#
# Pool views
#

class PoolView(generic.ObjectView):
    queryset = models.Pool.objects.all()

    def get_extra_context(self, request, instance):
        table = tables.PoolLeaseTable(instance.lease_to_pool.all())
        table.configure(request)

        return {
            'leases_table': table,
        }


class PoolListView(generic.ObjectListView):
    queryset = models.Pool.objects.annotate(
        lease_count=Count('lease_to_pool')
    )
    table = tables.PoolTable
    filterset = filtersets.PoolFilterSet
    filterset_form = forms.PoolFilterForm


class PoolEditView(generic.ObjectEditView):
    queryset = models.Pool.objects.all()
    form = forms.PoolForm


class PoolDeleteView(generic.ObjectDeleteView):
    queryset = models.Pool.objects.all()


#
# PoolLease views
#

class PoolLeaseView(generic.ObjectView):
    queryset = models.PoolLease.objects.all()


class PoolLeaseListView(generic.ObjectListView):
    queryset = models.PoolLease.objects.all()
    table = tables.PoolLeaseTable
    filterset = filtersets.PoolLeaseFilterSet
    filterset_form = forms.PoolLeaseFilterForm


class PoolLeaseEditView(generic.ObjectEditView):
    queryset = models.PoolLease.objects.all()
    form = forms.PoolLeaseForm


class PoolLeaseDeleteView(generic.ObjectDeleteView):
    queryset = models.PoolLease.objects.all()
