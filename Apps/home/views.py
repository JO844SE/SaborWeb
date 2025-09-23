from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import IntegrityError
from .models import *

# Create your views here.
def home(request):
    categoria = Category.objects.all()
    producto = Product.objects.all()
    return render(request, 'index.html', {'producto': producto, 'categoria': categoria})

def contact(request):
    return render(request, 'contact.html')

def login(request):
    return render(request, 'login.html')

def app(request):
    return render(request, 'App/base.html')

def dashboard(request):
    categoria = Category.objects.count()
    producto = Product.objects.count()
    return render(request, 'App/dashboard.html', {'categoria': categoria, 'producto': producto})


#-------------------------------
# Vistas para productos
#-------------------------------
def productosList(request):
    productos = Product.objects.all()
    return render(request, 'App/productos.html', {'productos': productos})

def productDelete(request, id):
    producto = Product.objects.get(id=id)
    producto.delete()
    return redirect('productos')

def registrarProducto(request):
    # Obtener todas las categorías para el formulario (tanto GET como POST)
    categorias = Category.objects.all()
    
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion')
        precio = request.POST.get('precio')
        imagen_url = request.POST.get('imagen')  # Ahora es una URL
        categoria_id = request.POST.get('categoria')

        # Validar que todos los campos requeridos estén presentes
        if not all([nombre, descripcion, precio, categoria_id, imagen_url]):
            return render(request, 'App/registrarProducto.html', {
                'categorias': categorias,
                'error': 'Todos los campos son obligatorios.',
                'nombre': nombre,
                'descripcion': descripcion,
                'precio': precio,
                'imagen': imagen_url,
                'categoria_id': categoria_id
            })

        try:
            # Validar precio
            precio_decimal = float(precio)
            if precio_decimal <= 0:
                raise ValueError("El precio debe ser mayor que 0")

            # Validar que la categoría existe
            categoria = Category.objects.get(id=categoria_id)


            # Crear el producto con la URL de imagen
            producto = Product.objects.create(
                name=nombre,
                description=descripcion,
                price=precio_decimal,
                image=imagen_url,  # Guardar la URL directamente
                category=categoria
            )
            return redirect('productos')
            
        except ValueError as e:
            return render(request, 'App/registrarProducto.html', {
                'categorias': categorias,
                'error': str(e),
                'nombre': nombre,
                'descripcion': descripcion,
                'precio': precio,
                'imagen': imagen_url,
                'categoria_id': categoria_id
            })
        except Category.DoesNotExist:
            return render(request, 'App/registrarProducto.html', {
                'categorias': categorias,
                'error': 'La categoría seleccionada no existe.',
                'nombre': nombre,
                'descripcion': descripcion,
                'precio': precio,
                'imagen': imagen_url
            })
        except Exception as e:
            return render(request, 'App/registrarProducto.html', {
                'categorias': categorias,
                'error': f'Error al registrar el producto: {str(e)}',
                'nombre': nombre,
                'descripcion': descripcion,
                'precio': precio,
                'imagen': imagen_url,
                'categoria_id': categoria_id
            })
    
    # GET request - mostrar formulario
    return render(request, 'App/registrarProducto.html', {'categorias': categorias})


def selectEdicionProducto(request, id):
    producto = Product.objects.get(id=id)
    categorias = Category.objects.all()
    return render(request, 'App/editarProducto.html', {'producto': producto, 'categorias': categorias})

def editarProducto(request):
    if request.method == 'POST':
        id = request.POST.get('id')
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion')
        precio = request.POST.get('precio')
        imagen_url = request.POST.get('imagen')
        categoria_id = request.POST.get('categoria')

        try:
            # Validar precio
            precio_decimal = float(precio)
            if precio_decimal <= 0:
                raise ValueError("El precio debe ser mayor que 0")

            # Validar que la categoría existe
            categoria = Category.objects.get(id=categoria_id)

            # Validar URL de imagen
            if not imagen_url.startswith(('http://', 'https://')):
                raise ValueError("La URL de la imagen debe comenzar con http:// o https://")

            # Actualizar el producto
            producto = Product.objects.get(id=id)
            producto.name = nombre
            producto.description = descripcion
            producto.price = precio_decimal
            producto.image = imagen_url
            producto.category = categoria
            producto.save()
            
            messages.success(request, f'El producto "{nombre}" se ha actualizado exitosamente.')
            return redirect('productos')
            
        except ValueError as e:
            messages.error(request, str(e))
            return redirect('selectEdicionProducto', id=id)
        except Category.DoesNotExist:
            messages.error(request, 'La categoría seleccionada no existe.')
            return redirect('selectEdicionProducto', id=id)
        except Product.DoesNotExist:
            messages.error(request, 'El producto no existe.')
            return redirect('productos')
        except Exception as e:
            messages.error(request, f'Error al actualizar el producto: {str(e)}')
            return redirect('selectEdicionProducto', id=id)
    
    return redirect('productos')


#-------------------------------
# Vistas para categorías
#-------------------------------
def registrarCategoria(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion')

        categoria = Category.objects.create(
            name=nombre,
            description=descripcion
        )
        return redirect('categoriaList')
    return render(request, 'App/registrarCategoria.html')


def categoriaList(request):
    categorias = Category.objects.all()
    return render(request, 'App/categorias.html', {'categorias': categorias})

def selectEdicioncategoria(request, id):
    categoria = Category.objects.get(id=id)
    return render(request, 'App/editarCategoria.html', {'categoria': categoria})

def editarCategoria(request):
    if request.method == 'POST':
        id = request.POST.get('id')
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion')

        categoria = Category.objects.get(id=id)
        categoria.name = nombre
        categoria.description = descripcion
        categoria.save()
        return redirect('categoriaList')
    return render(request, 'App/editarCategoria.html')


def categoriaDelete(request, id):
    categoria = Category.objects.get(id=id)
    categoria.delete()
    return redirect('categoriaList')





#-------------------------------
# Vistas para autenticación
#-------------------------------
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