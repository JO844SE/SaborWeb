
from django.db import models
# Create your models here.

class User(models.Model):
    id = models.AutoField(primary_key=True)  # PK autoincremental
    username = models.CharField(max_length=50, unique=True)
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
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, db_column='category_id')
    created_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "Productos"

    def __str__(self):
        return self.name