from django.shortcuts import render, redirect
from django.contrib import messages
from Apps.home.models import Product, Order, OrderItem, User as AppUser

# Utility function to clear existing messages
def clear_messages(request):
    list(messages.get_messages(request))

def _get_cart(request):
    return request.session.get('cart', {})

def _save_cart(request, cart):
    request.session['cart'] = cart


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
    # Calcular la cantidad total de productos en el carrito
    session_cart = request.session.get('cart', {})
    total_quantity = sum(int(q) for q in session_cart.values()) if session_cart else 0

    return render(request, 'App/cart.html', {'items': items, 'total': total, 'total_quantity': total_quantity})


def cart_add(request, product_id):
    # For the shop, prefer Django auth user (request.user)
    if not request.user.is_authenticated:
        clear_messages(request)
        messages.warning(request, 'Debes iniciar sesión para agregar al carrito')
        return redirect('Tienda:login')

    cart = _get_cart(request)
    key = str(product_id)
    cart[key] = cart.get(key, 0) + 1
    _save_cart(request, cart)
    clear_messages(request)
    messages.success(request, 'Producto agregado al carrito')
    return redirect('Tienda:home')


def cart_remove(request, product_id):
    cart = _get_cart(request)
    key = str(product_id)
    if key in cart:
        del cart[key]
        _save_cart(request, cart)
        request.session.modified = True
        clear_messages(request)
        messages.success(request, 'Producto eliminado del carrito')
    else:
        clear_messages(request)
        messages.warning(request, 'El producto no estaba en el carrito')
    return redirect('shop:cart')


def checkout(request):
    if not request.user.is_authenticated:
        clear_messages(request)
        messages.warning(request, 'Debes iniciar sesión para realizar el checkout')
        return redirect('Tienda:login')

    cart = _get_cart(request)
    if not cart:
        clear_messages(request)
        messages.error(request, 'El carrito está vacío')
        return redirect('shop:cart')

    if request.method != 'POST':
        clear_messages(request)
        messages.warning(request, 'Método inválido para checkout')
        return redirect('shop:cart')

    # Leer los campos proporcionados por el cliente desde el formulario del carrito
    nombreApellido = (request.POST.get('nombreApellido') or '').strip()
    telefono = (request.POST.get('telefono') or '').strip()

    # Validación básica: requerir nombre y teléfono
    if not nombreApellido:
        clear_messages(request)
        messages.error(request, 'Por favor ingresa tu nombre y apellido')
        return redirect('shop:cart')
    if not telefono:
        clear_messages(request)
        messages.error(request, 'Por favor ingresa un número de teléfono')
        return redirect('shop:cart')
    # Normalize/limit phone length to match model (max_length=8)
    if len(telefono) > 8:
        clear_messages(request)
        messages.error(request, 'El número de teléfono no debe exceder 8 dígitos')
        return redirect('shop:cart')

    app_user = AppUser.objects.get(pk=request.user.pk)
    order = Order.objects.create(
        user=app_user,
        username=request.user.username,
        status='PENDING',
        total=0,
        nombreApellido=nombreApellido,
        telefono=telefono,
    )

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
    
    return redirect('shop:order_list_client')


def order_list(request):
    if not request.user.is_authenticated:
        clear_messages(request)
        messages.warning(request, 'Debes iniciar sesión para ver tus pedidos')
        return redirect('Tienda:login')

    username = getattr(request.user, 'username', None)
    orders = Order.objects.filter(username=username).order_by('created_at')

    # Calcular la cantidad total de productos en el carrito
    session_cart = request.session.get('cart', {})
    total_quantity = sum(int(q) for q in session_cart.values()) if session_cart else 0
    return render(request, 'App/ordersClient.html', {'orders': orders, 'total_quantity': total_quantity})


def order_detail(request, id):
    if not request.user.is_authenticated:
        clear_messages(request)
        messages.warning(request, 'Debes iniciar sesión para ver el pedido')
        return redirect('Tienda:login')

    username = getattr(request.user, 'username', None)
    try:
        order = Order.objects.get(id=id, username=username)
    except Order.DoesNotExist:
        clear_messages(request)
        messages.error(request, 'Pedido no encontrado')
        return redirect('shop:order_listClient')
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
    
    # Calcular la cantidad total de productos en el carrito
    session_cart = request.session.get('cart', {})
    total_quantity = sum(int(q) for q in session_cart.values()) if session_cart else 0
    return render(request, 'App/order_detailClient.html', {'order': order, 'items': items, 'total_quantity': total_quantity})




def cart_sumar(request, product_id):
    # For the shop, prefer Django auth user (request.user)
    if not request.user.is_authenticated:
        clear_messages(request)
        messages.warning(request, 'Debes iniciar sesión para agregar al carrito')
        return redirect('Tienda:login')

    cart = _get_cart(request)
    key = str(product_id)
    cart[key] = cart.get(key, 0) + 1
    _save_cart(request, cart)
    clear_messages(request)
    messages.success(request, 'Producto agregado al carrito')
    return redirect('shop:cart')


def cart_restar(request, product_id):
    # For the shop, prefer Django auth user (request.user)
    if not request.user.is_authenticated:
        clear_messages(request)
        messages.warning(request, 'Debes iniciar sesión para agregar al carrito')
        return redirect('Tienda:login')

    cart = _get_cart(request)
    key = str(product_id)
    qty = cart.get(key, 0)

    if qty <= 1:
        return redirect('shop:cart')
    
    qty -= 1
    cart[key] = qty

    _save_cart(request, cart)
    request.session.modified = True
    clear_messages(request)
    messages.success(request, 'Producto restado del carrito')
    return redirect('shop:cart')