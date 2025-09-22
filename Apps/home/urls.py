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


   path('productos/', productosList, name='productos'),
   path('categoriaList/', categoriaList, name='categoriaList'),
]
