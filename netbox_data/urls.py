from django.urls import path
from netbox.views.generic import ObjectChangeLogView

from . import models, views

urlpatterns = (

    # Device Info Manager
    path('deviceInfo/', views.DeviceInfoListView.as_view(), name='deviceinfo_list'),
    path('deviceInfo/add/', views.DeviceInfoEditView.as_view(), name='deviceinfo_add'),
    path('deviceInfo/delete/', views.DeviceInfoBulkDeleteView.as_view(), name='deviceinfo_bulk_delete'),
    path('deviceInfo/<int:pk>/', views.DeviceInfoView.as_view(), name='deviceinfo'),
    path('deviceInfo/<int:pk>/edit/', views.DeviceInfoEditView.as_view(), name='deviceinfo_edit'),
    path('deviceInfo/<int:pk>/delete/', views.DeviceInfoDeleteView.as_view(), name='deviceinfo_delete'),
    path('deviceInfo/<int:pk>/changelog/', ObjectChangeLogView.as_view(), name='deviceinfo_changelog', kwargs={
        'model': models.DeviceInfo
    }),

    # Vlan Info Manager
    path('vlanInfo/', views.VlanInfoListView.as_view(), name='vlaninfo_list'),
    path('vlanInfo/add/', views.VlanInfoEditView.as_view(), name='vlaninfo_add'),
    path('vlanInfo/delete/', views.VlanInfoBulkDeleteView.as_view(), name='vlaninfo_bulk_delete'),
    path('vlanInfo/<int:pk>/', views.VlanInfoView.as_view(), name='vlaninfo'),
    path('vlanInfo/<int:pk>/edit/', views.VlanInfoEditView.as_view(), name='vlaninfo_edit'),
    path('vlanInfo/<int:pk>/delete/', views.VlanInfoDeleteView.as_view(), name='vlaninfo_delete'),
    path('vlanInfo/<int:pk>/changelog/', ObjectChangeLogView.as_view(), name='vlaninfo_changelog', kwargs={
        'model': models.VlanInfo
    }),

)