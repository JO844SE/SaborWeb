from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import get_user_model
from Apps.home.models import Product, Order, OrderItem, User as AppUser
from .models import Cart, CartItem

User = get_user_model()


def _get_cart(request):
    return request.session.get('cart', {})


def _save_cart(request, cart):
    request.session['cart'] = cart
    request.session.modified = True
    # Persist to DB for authenticated django user
    try:
        if request.user.is_authenticated:
            save_session_cart_to_db(request.user, cart)
    except Exception:
        pass


def save_session_cart_to_db(user, cart):
    # cart: dict of str(product_id)->qty
    if not cart:
        # remove existing cart if empty
        Cart.objects.filter(user=user).delete()
        return
    cart_obj, _ = Cart.objects.get_or_create(user=user)
    # clear existing items
    cart_obj.items.all().delete()
    for pid, qty in cart.items():
        try:
            prod = Product.objects.get(id=pid)
            CartItem.objects.create(cart=cart_obj, product=prod, quantity=qty, price=prod.price)
        except Product.DoesNotExist:
            continue


def cart_view(request):
    cart = _get_cart(request)
    items = []
    total = 0
    for pid, qty in cart.items():
        try:
            prod = Product.objects.get(id=pid)
            line = prod.price * qty
            items.append({'product': prod, 'quantity': qty, 'line_total': line})
            total += line
        except Product.DoesNotExist:
            continue
    return render(request, 'App/cart.html', {'items': items, 'total': total})


def cart_add(request, product_id):
    # For the shop, prefer Django auth user (request.user)
    if not request.user.is_authenticated:
        messages.warning(request, 'Debes iniciar sesión para agregar al carrito')
        return redirect('Tienda:login')

    cart = _get_cart(request)
    key = str(product_id)
    cart[key] = cart.get(key, 0) + 1
    _save_cart(request, cart)
    messages.success(request, 'Producto agregado al carrito')
    return redirect('Tienda:home')


def cart_remove(request, product_id):
    cart = _get_cart(request)
    key = str(product_id)
    if key in cart:
        del cart[key]
        _save_cart(request, cart)
    return redirect('shop:cart')


def checkout(request):
    # Require Django-authenticated user for checkout and save their username on the order
    if not request.user.is_authenticated:
        messages.warning(request, 'Debes iniciar sesión para realizar el checkout')
        return redirect('Tienda:login')

    cart = _get_cart(request)
    if not cart:
        messages.error(request, 'El carrito está vacío')
        return redirect('shop:cart')

    username = getattr(request.user, 'username', None)
    email = getattr(request.user, 'email', None)

    # Try to map Django user to the local AppUser (by email first, then username).
    app_user = None
    try:
        if email:
            app_user = AppUser.objects.filter(email=email).first()
        if not app_user and username:
            app_user = AppUser.objects.filter(username=username).first()
        # If no AppUser found, create one so FK constraint is satisfied
        if not app_user:
            from uuid import uuid4
            safe_email = email if email else f'auto_{uuid4().hex}@local'
            app_user = AppUser.objects.create(username=username or f'user_{request.user.id}', email=safe_email, password='')
    except Exception:
        app_user = None

    # Create order and store the username and link the local user (to satisfy DB FK constraint)
    order = Order.objects.create(user=app_user, username=username, status='PENDING', total=0)
    total = 0
    for pid, qty in cart.items():
        try:
            product = Product.objects.get(id=pid)
            item = OrderItem.objects.create(order=order, product=product, quantity=qty, price=product.price)
            total += item.line_total()
        except Product.DoesNotExist:
            continue
    order.total = total
    order.save()
    request.session['cart'] = {}
    request.session.modified = True
    messages.success(request, f'Pedido #{order.id} creado correctamente')
    return redirect('Tienda:home')


def order_list(request):
    if not request.user.is_authenticated:
        messages.warning(request, 'Debes iniciar sesión para ver tus pedidos')
        return redirect('Tienda:login')

    username = getattr(request.user, 'username', None)
    orders = Order.objects.filter(username=username).order_by('-created_at')
    return render(request, 'App/orders.html', {'orders': orders})


def order_detail(request, id):
    if not request.user.is_authenticated:
        messages.warning(request, 'Debes iniciar sesión para ver el pedido')
        return redirect('Tienda:login')

    username = getattr(request.user, 'username', None)
    try:
        order = Order.objects.get(id=id, username=username)
    except Order.DoesNotExist:
        messages.error(request, 'Pedido no encontrado')
        return redirect('shop:order_list')
    # Build a list of items with product info (name, price, quantity, line_total)
    items = []
    for it in order.items.select_related('product').all():
        prod = getattr(it, 'product', None)
        if prod:
            items.append({
                'product_id': prod.id,
                'name': prod.name,
                'price': it.price,
                'quantity': it.quantity,
                'line_total': it.line_total(),
            })
    return render(request, 'App/order_detail.html', {'order': order, 'items': items})
