from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('inventory/', views.product_list, name='product_list'),
    path('shop/', views.shop, name='shop'),
    path('product/create/', views.product_create, name='product_create'),
    path('product/update/<int:pk>/', views.product_update, name='product_update'),
    path('product/delete/<int:pk>/', views.product_delete, name='product_delete'),
    path('backup/', views.backup, name='backup'),
    path('manage-roles/', views.manage_roles, name='manage_roles'),
    path('income/', views.income, name='income'),
    path('add_product/', views.add_product, name='add_product'),
    path('product/detail/<int:product_id>/', views.product_detail, name='product_detail'),
]