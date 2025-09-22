from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(User)  # Aquí debes registrar tus modelos, por ejemplo: admin.site.register(User)
admin.site.register(Category)
admin.site.register(Product)