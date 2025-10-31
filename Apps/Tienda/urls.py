from django.urls import path, include
from .views import *

app_name = 'Tienda'

urlpatterns = [
    path('', home, name='home'),
    path('signup/', SignUpView.as_view(), name='signup'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('contact/', contact, name='contact'),
]
