from django.urls import path
from netbox.views.generic import ObjectChangeLogView

from . import models, views

urlpatterns = (

    # Device Info Manager
    path('device/', views.DeviceInfoListView.as_view(), name='deviceinfo_list'),
    path('device/add/', views.DeviceInfoEditView.as_view(), name='deviceinfo_add'),
    path('device/delete/', views.DeviceInfoBulkDeleteView.as_view(), name='deviceinfo_bulk_delete'),
    path('device/<int:pk>/', views.DeviceInfoView.as_view(), name='deviceinfo'),
    path('device/<int:pk>/edit/', views.DeviceInfoEditView.as_view(), name='deviceinfo_edit'),
    path('device/<int:pk>/delete/', views.DeviceInfoDeleteView.as_view(), name='deviceinfo_delete'),
    path('device/<int:pk>/changelog/', ObjectChangeLogView.as_view(), name='deviceinfo_changelog', kwargs={
        'model': models.DeviceInfo
    }),

    # Vlan Info Manager
    path('vlan/', views.VlanInfoListView.as_view(), name='vlaninfo_list'),
    path('vlan/add/', views.VlanInfoEditView.as_view(), name='vlaninfo_add'),
    path('vlan/delete/', views.VlanInfoBulkDeleteView.as_view(), name='vlaninfo_bulk_delete'),
    path('vlan/<int:pk>/', views.VlanInfoView.as_view(), name='vlaninfo'),
    path('vlan/<int:pk>/edit/', views.VlanInfoEditView.as_view(), name='vlaninfo_edit'),
    path('vlan/<int:pk>/delete/', views.VlanInfoDeleteView.as_view(), name='vlaninfo_delete'),
    path('vlan/<int:pk>/changelog/', ObjectChangeLogView.as_view(), name='vlaninfo_changelog', kwargs={
        'model': models.VlanInfo
    }),

)