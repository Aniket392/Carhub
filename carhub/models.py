from django.contrib.auth.models import User
from django.db import models
from datetime import datetime
from datetime import timedelta

class timestamp(models.Model):
    created_at = models.DateTimeField(default = datetime.now())
    updated_at = models.DateTimeField(default = datetime.now())
    is_active = models.BooleanField(default = True)
    created_by = models.CharField(default = None, max_length = 40)
    updated_by = models.CharField(default = None, max_length = 40)

    class Meta:
        abstract = True

class Category(timestamp):
    name = models.CharField(max_length=32, unique=True)

    def __str__(self):
        return self.name

class City(timestamp):
    name = models.CharField(max_length=32, unique=True)

    def __str__(self):
        return self.name

class Car(timestamp):
    brand = models.CharField(max_length=50)
    modelName = models.CharField(max_length=50)
    year = models.CharField(max_length=50)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    price = models.PositiveIntegerField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    photo = models.ImageField(upload_to='cars')

    def __str__(self):
        return str(self.brand + self.modelName)

class Order(timestamp):
    ORDER_STATUS = [
        ('BKD', 'Booked'),
        ('CAN', 'Cancelled'),
        ('COM', 'Completed'),
    ]
    userid = models.ForeignKey(User, on_delete=models.CASCADE)
    car =  models.ForeignKey(Car, on_delete=models.CASCADE, related_name='car_detail')
    orderDateFrom =  models.DateTimeField(default = datetime.now())
    orderDateExpire =  models.DateTimeField(default = datetime.now()+ timedelta(hours=1))
    totalOrderCost = models.PositiveIntegerField()
    status = models.CharField(max_length=3, choices=ORDER_STATUS, default='BKD')

    def __str__(self):
        return str(self.userid + self.order)

class UserProxy(timestamp):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_validated = models.BooleanField(default=False)
    dl = models.ImageField(upload_to='dl')
