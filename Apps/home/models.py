
from django.db import models
from django.core.exceptions import ValidationError

class User(models.Model):
    id = models.AutoField(primary_key=True)  # PK autoincremental
    username = models.CharField(max_length=50)
    email = models.EmailField(max_length=100, unique=True)
    password = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "Usuarios"

    def __str__(self):
        return self.username



# -------------------------------
# Modelo de categoría
# -------------------------------
class Category(models.Model):
    id = models.AutoField(primary_key=True)  # PK autoincremental explícita
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "Categorias"

    def __str__(self):
        return self.name


# -------------------------------
# Modelo de producto
# -------------------------------
class Product(models.Model):
    id = models.AutoField(primary_key=True)  # PK autoincremental explícita
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.RESTRICT, db_column='category_id')
    created_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "Productos"

    def __str__(self):
        return self.name


# -------------------------------
# Modelo de pedido (Order) y items del pedido (OrderItem)
# -------------------------------
class Order(models.Model):
    STATUS_PENDING = 'PENDING'
    STATUS_PROCESSING = 'PROCESSING'
    STATUS_READY = 'READY'
    STATUS_DELIVERED = 'DELIVERED'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pendiente'),
        (STATUS_PROCESSING, 'En proceso'),
        (STATUS_READY, 'Listo'),
        (STATUS_DELIVERED, 'Entregado'),
    ]

    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    username = models.CharField(max_length=150, null=True, blank=True)
    nombreApellido = models.CharField(max_length=100, null=True)
    telefono = models.CharField(max_length=8, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'Pedidos'

    def __str__(self):
        return f'Pedido #{self.id} - {self.status}'


class OrderItem(models.Model):
    id = models.AutoField(primary_key=True)
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.RESTRICT)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = 'Pedido_Items'

    def __str__(self):
        return f'{self.quantity} x {self.product.name} (Pedido {self.order_id})'

    def line_total(self):
        return (self.price or 0) * (self.quantity or 0)