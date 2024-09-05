from django.urls import path
from netbox.views.generic import ObjectChangeLogView

from . import models, views

urlpatterns = (

    # Data Manager
    path('deviceInfo/', views.DeviceInfoListView.as_view(), name='deviceinfo_list'),
    path('deviceInfo/add/', views.DeviceInfoEditView.as_view(), name='deviceinfo_add'),
    path('deviceInfo/delete/', views.DeviceInfoBulkDeleteView.as_view(), name='deviceinfo_bulk_delete'),
    path('deviceInfo/<int:pk>/', views.DeviceInfoView.as_view(), name='deviceInfo'),
    path('deviceInfo/<int:pk>/edit/', views.DeviceInfoEditView.as_view(), name='deviceinfo_edit'),
    path('deviceInfo/<int:pk>/delete/', views.DeviceInfoDeleteView.as_view(), name='deviceinfo_delete'),
    path('deviceInfo/<int:pk>/changelog/', ObjectChangeLogView.as_view(), name='deviceinfo_changelog', kwargs={
        'model': models.DeviceInfo
    }),

)