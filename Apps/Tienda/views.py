from django.shortcuts import render
from django.contrib.auth.forms import UserCreationForm
from django.views.generic import CreateView
from django.urls import reverse_lazy

from Apps.home.models import Category, Product
from Apps.shop.models import CartItem

class SignUpView(CreateView):
    form_class = UserCreationForm
    template_name = 'registration/signup.html'
    success_url = reverse_lazy('Tienda:home')



def home(request):
    categoria = Category.objects.all()
    producto = Product.objects.all()

    session_cart = request.session.get('cart', {})
    total_quantity = sum(int(q) for q in session_cart.values()) if session_cart else 0

    return render(request, 'index.html', {'producto': producto, 'categoria': categoria, 'total_quantity': total_quantity})


def contact(request):
    session_cart = request.session.get('cart', {})
    total_quantity = sum(int(q) for q in session_cart.values()) if session_cart else 0
    return render(request, 'contact.html', {'total_quantity': total_quantity})