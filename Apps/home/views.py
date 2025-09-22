from django.shortcuts import render, redirect
from .models import *

# Create your views here.
def home(request):
    categoria = Category.objects.all().all()
    producto = Product.objects.all().all()
    return render(request, 'index.html', {'producto': producto, 'categoria': categoria})

def contact(request):
    return render(request, 'contact.html')

def login(request):
    return render(request, 'login.html')

def app(request):
    return render(request, 'App/base.html')

def dashboard(request):
    return render(request, 'App/dashboard.html')


def productosList(request):
    productos = Product.objects.all()
    return render(request, 'App/productos.html', {'productos': productos})


def categoriaList(request):
    categorias = Category.objects.all()
    return render(request, 'App/categorias.html', {'categorias': categorias})



def loginview(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        usuario = User.objects.filter(email= email, password=password).first()
        if usuario:
            #autenticacion exitosa
            request.session['user_id'] = usuario.id
            request.session['user_authenticated'] = True
            return redirect('dashboard')
        else:
            return render(request, 'login.html', {'error': 'Credenciales invalidas'})
    else:
        return render(request, 'login.html')


def logout(request):
    request.session.flush()
    return redirect('home')