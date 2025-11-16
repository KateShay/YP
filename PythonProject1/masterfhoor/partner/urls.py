from django.urls import path
from . import views

app_name = 'partners'

urlpatterns = [
    path('', views.PartnerListView.as_view(), name='partner_list'),
    path('add/', views.PartnerCreateView.as_view(), name='partner_add'),
    path('<int:pk>/edit/', views.PartnerUpdateView.as_view(), name='partner_edit'),
    path('<int:pk>/sales-history/', views.SalesHistoryView.as_view(), name='sales_history'),
    path('<int:partner_id>/discount/', views.calculate_discount_api, name='calculate_discount'),
    path('calculate-material/', views.calculate_material_api, name='calculate_material'),
]