from django.urls import path

from netbox.views.generic import ObjectChangeLogView
from . import models, views


urlpatterns = (

    # Pool Manager
    path('pool/', views.PoolListView.as_view(), name='pool_list'),
    path('pool/add/', views.PoolEditView.as_view(), name='pool_add'),
    path('pool/<int:pk>/', views.PoolView.as_view(), name='pool'),
    path('pool/<int:pk>/edit/', views.PoolEditView.as_view(), name='pool_edit'),
    path('pool/<int:pk>/delete/', views.PoolDeleteView.as_view(), name='pool_delete'),
    path('pool/<int:pk>/changelog/', ObjectChangeLogView.as_view(), name='pool_changelog', kwargs={
        'model': models.Pool
    }),

    # Pool Manager lease
    path('lease/', views.PoolLeaseListView.as_view(), name='poollease_list'),
    path('lease/add/', views.PoolLeaseEditView.as_view(), name='poollease_add'),
    path('lease/<int:pk>/', views.PoolLeaseView.as_view(), name='poollease'),
    path('lease/<int:pk>/edit/', views.PoolLeaseEditView.as_view(), name='poollease_edit'),
    path('lease/<int:pk>/delete/', views.PoolLeaseDeleteView.as_view(), name='poollease_delete'),
    path('lease/<int:pk>/changelog/', ObjectChangeLogView.as_view(), name='poollease_changelog', kwargs={
        'model': models.PoolLease
    }),

)
