from django.urls import path
from .views import *

urlpatterns = [
   path('', home, name='home'),
   path('contact/', contact, name='contact'),
   path('login/', login, name='login'),
   path('loginview/', loginview, name='loginview'),
   path('app/', app, name='app'),
   path('logout/', logout, name='logout'),
   path('dashboard/', dashboard, name='dashboard'),

   #-------------------------------
   # Rutas para productos
   #-------------------------------
   path('productos/', productosList, name='productos'),
   path('registrarProducto/', registrarProducto, name='registrarProducto'),
   path('productDelete/<int:id>/', productDelete, name='productDelete'),
   path('selectEdicionProducto/<int:id>/', selectEdicionProducto, name='selectEdicionProducto'),
   path('editarProducto/', editarProducto, name='editarProducto'),





   #-------------------------------
   # Rutas para categorías
   #-------------------------------
   path('registrarCategoria/', registrarCategoria, name='registrarCategoria'),
   path('categoriaList/', categoriaList, name='categoriaList'),
   path('selectEdicioncategoria/<int:id>/', selectEdicioncategoria, name='selectEdicioncategoria'),
   path('editarCategoria/', editarCategoria, name='editarCategoria'),
   path('categoriaDelete/<int:id>/', categoriaDelete, name='categoriaDelete'),
]
