from django.contrib import admin
from .models import *

admin.site.register([Category, City, Car, Order, UserProxy, CarDetails])