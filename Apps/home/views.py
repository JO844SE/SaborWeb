from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse
from functools import wraps
from .models import *
import bcrypt

#-------------------------------
# Sistema de Autenticación Personalizado
#-------------------------------

def is_authenticated(request):
    """
    Verifica si el usuario está autenticado basándose en la sesión
    """
    return 'user_id' in request.session and request.session['user_id'] is not None

def login_required_custom(login_url='/login/'):
    """
    Decorador personalizado que verifica si el usuario está autenticado
    Si no está autenticado, redirige al login
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if is_authenticated(request):
                return view_func(request, *args, **kwargs)
            else:
                storage = messages.get_messages(request)
                storage.used = True
                messages.warning(request, "Debes iniciar sesión para acceder a esta página")
                return redirect(login_url)
        return _wrapped_view
    return decorator

def get_authenticated_user(request):
    """
    Obtiene el usuario autenticado de la sesión
    Retorna el objeto User o None si no está autenticado
    """
    if is_authenticated(request):
        try:
            user_id = request.session['user_id']
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            # Si el usuario no existe, limpiar la sesión
            if 'user_id' in request.session:
                del request.session['user_id']
    return None


# Create your views here.
def home(request):
    categoria = Category.objects.all()
    producto = Product.objects.all()
    return render(request, 'index.html', {'producto': producto, 'categoria': categoria})

def contact(request):
    return render(request, 'contact.html')

def login(request):
    return render(request, 'login.html')

@login_required_custom()
def dashboard(request):
    categoria = Category.objects.count()
    producto = Product.objects.count()
    user = get_authenticated_user(request)
    return render(request, 'App/dashboard.html', {
        'categoria': categoria, 
        'producto': producto,
        'user': user
    })


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
        imagen_url = request.POST.get('imagen')  # es una URL
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
    
    # mostrar formulario
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
# Vistas de usuario
#-------------------------------

def registrarusuario(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        correo = request.POST.get('email')
        password = request.POST.get('password')

        # Convertimos la contraseña a bytes (bcrypt trabaja con bytes
        passwordHash = password.encode('utf-8')
        # Generamos un "salt" (valor aleatorio para reforzar el hash)
        salt = bcrypt.gensalt()
        # Hasheamos la contraseña
        hashed = bcrypt.hashpw(passwordHash, salt)

        usuario = User.objects.create(
            username = nombre,
            email = correo,
            password = hashed.decode('utf-8') #guardar como string en la DB
        ) 
        return redirect('listUser')
    return render(request, 'App/registrarUsuarios.html' )



def listUser(request):
    usuario = User.objects.all()
    return render(request, 'App/usuarios.html', {'usuario': usuario })


def selectEdicionUser(request, id):
    usuario = User.objects.get(id=id)
    return render(request, 'App/editarusuarios.html', {'usuario': usuario} )


def editUser(request):
    if request.method == 'POST':
        id = request.POST.get('id')
        nombre = request.POST.get('nombre')
        correo = request.POST.get('email')
        password = request.POST.get('password')

        # Convertimos la contraseña a bytes (bcrypt trabaja con bytes
        passwordHash = password.encode('utf-8')
        # Generamos un "salt" (valor aleatorio para reforzar el hash)
        salt = bcrypt.gensalt()
        # Hasheamos la contraseña
        hashed = bcrypt.hashpw(passwordHash, salt)

        user = User.objects.get(id=id)
        user.username = nombre
        user.email = correo
        user.password = hashed.decode('utf-8')
        user.save()

        return redirect('listUser')
    return render(request, 'App/editarusuarios.html')



def deleteUser(request, id):
    id = User.objects.get(id=id)
    id.delete()
    return redirect('listUser')





#-------------------------------
# Vistas para autenticación
#-------------------------------
def loginview(request):
    # Si ya está autenticado, redirigir al dashboard
    if is_authenticated(request):
        return redirect('dashboard')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Validar campos vacíos
        if not email or not password:
            messages.error(request, 'Por favor, ingrese email y contraseña')
            return render(request, 'login.html')

        try:
            usuario = User.objects.filter(email=email).first()
            if usuario:
                # Hash guardado en la base de datos (es string, lo convertimos a bytes)
                hashed = usuario.password.encode('utf-8')
                # Verificamos contraseña ingresada vs hash
                if bcrypt.checkpw(password.encode('utf-8'), hashed):
                    # Autenticación exitosa
                    request.session['user_id'] = usuario.id
                    messages.success(request, f'Bienvenido {usuario.username}!')
                    return redirect('dashboard')
                else:
                    messages.error(request, 'Email o contraseña incorrectos')
            else:
                messages.error(request, 'Email o contraseña incorrectos')
        except Exception as e:
            messages.error(request, 'Error en el sistema de autenticación')
    
    return render(request, 'login.html')


def logout(request):
    request.session.flush()
    return redirect('home')