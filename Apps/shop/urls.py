from django.urls import path
from . import views

app_name = 'shop'

urlpatterns = [
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<int:product_id>/', views.cart_add, name='cart_add'),
    path('cart/sumar/<int:product_id>/', views.cart_sumar, name='cart_sumar'),
    path('cart/restar/<int:product_id>/', views.cart_restar, name='cart_restar'),
    path('cart/remove/<int:product_id>/', views.cart_remove, name='cart_remove'),
    path('checkout/', views.checkout, name='checkout'),
    path('orders/', views.order_list, name='order_list_client'),
    path('orders/<int:id>/', views.order_detail, name='order_detail'),
]
