from django.contrib.auth.models import User
from django.db import models
from datetime import datetime
from datetime import timedelta
from cloudinary.models import CloudinaryField
import datetime as dt
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

class CarDetails(timestamp):
    year = models.IntegerField(('year'), choices=[(r,r) for r in range(1950, dt.date.today().year+1)], default=dt.date.today().year)
    odometer = models.IntegerField(default = 0)
    fuel = models.CharField(default=None, max_length=40)
    manufacturer = models.CharField(default=None, max_length=40)
    drive = models.CharField(default='rwd', max_length=40)
    cylinders = models.CharField(default='4 cylinders', max_length=40)
    price_by_model = models.IntegerField()
    price_by_user = models.IntegerField()
    conflict = models.BooleanField(default=False)
    conflict_manually_resolved = models.BooleanField(default=False, blank = True, null = True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.manufacturer + self.user.first_name)

class Car(timestamp):
    brand = models.CharField(max_length=50) 
    modelName = models.CharField(max_length=50)
    year = models.CharField(max_length=50)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    details = models.ForeignKey(CarDetails, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    photo = CloudinaryField('img', default = None)
    # rc = CloudinaryField('rc', default = None)
    # photo = models.ImageField(upload_to = 'cars')
    rc = models.ImageField(upload_to = 'rc')
    is_valid = models.BooleanField(default=False, blank=True, null=True)

    def __str__(self):
        return str(self.brand + self.modelName)

class Order(timestamp):
    ORDER_STATUS = [
        ('BKD', 'Booked'),
        ('CAN', 'Cancelled'),
        ('COM', 'Completed'),
        ('PEND', 'Pending'),
        ('FAIL', 'Failed'),
    ]
    userid = models.ForeignKey(User, on_delete=models.CASCADE)
    car =  models.ForeignKey(Car, on_delete=models.CASCADE, related_name='car_detail')
    orderDateFrom =  models.DateTimeField(default = datetime.now())
    orderDateExpire =  models.DateTimeField(default = datetime.now()+ timedelta(hours=1))
    totalOrderCost = models.PositiveIntegerField()
    bookingDate = models.DateTimeField(default = datetime.now())
    status = models.CharField(max_length=4, choices=ORDER_STATUS, default='PEND')

    def __str__(self):
        return str(self.userid.first_name + self.car.brand)

class UserProxy(timestamp):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_valid_renter = models.BooleanField(default=False)
    is_valid_rider = models.BooleanField(default=False)
    dl = models.ImageField(upload_to='dl', blank = True)
    # dl = CloudinaryField('dl', default = None)
    dl_no = models.CharField(default=None, max_length = 15, null=True, blank = True)
    account_no = models.CharField(default=None, max_length=11)
    IFSC = models.CharField(default=None, max_length=20)
    holder_name = models.CharField(default=None, max_length=40)

    def __str__(self):
        return str(self.user.username)


