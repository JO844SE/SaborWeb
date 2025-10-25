from django.shortcuts import render
from django.contrib.auth.forms import UserCreationForm
from django.views.generic import CreateView
from django.urls import reverse_lazy

from Apps.home.models import Category, Product

class SignUpView(CreateView):
    form_class = UserCreationForm
    template_name = 'registration/signup.html'
    success_url = reverse_lazy('Tienda:home')



def home(request):
    categoria = Category.objects.all()
    producto = Product.objects.all()
    return render(request, 'index.html', {'producto': producto, 'categoria': categoria})

# Create your views here.
