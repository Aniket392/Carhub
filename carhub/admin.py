from django.contrib import admin
from django.utils.html import format_html
from django.contrib.admin import DateFieldListFilter
from .models import *

# admin.site.register([City, Car, Order, UserProxy, CarDetails])

class CategoryAdmin(admin.ModelAdmin):  
    def __init__(self, model, admin_site):
        self.list_display = [field.name for field in model._meta.fields]
        super(CategoryAdmin, self).__init__(model, admin_site)

class CityAdmin(admin.ModelAdmin):  
    def __init__(self, model, admin_site):
        self.list_display = [field.name for field in model._meta.fields]
        super(CityAdmin, self).__init__(model, admin_site)
class CarAdmin(admin.ModelAdmin):  
    search_fields = ('brand',)

    def __init__(self, model, admin_site):
        self.list_display = [field.name if field.name != 'photo' else 'get_url' for field in model._meta.fields]
        super(CarAdmin, self).__init__(model, admin_site)

    def get_url(self, obj):
        return format_html("<a href='{url}'>{img}</a>", url=obj.photo.url, img = obj.photo.public_id)

    get_url.short_description = 'Car Photo'
    get_url.allow_tags = True


class OrderAdmin(admin.ModelAdmin):  
    list_filter = ('status',('bookingDate', DateFieldListFilter),)
    def __init__(self, model, admin_site):
        self.list_display = [field.name for field in model._meta.fields]
        super(OrderAdmin, self).__init__(model, admin_site)

class UserProxyAdmin(admin.ModelAdmin):
    def __init__(self, model, admin_site):
        self.list_display = [field.name for field in model._meta.fields]
        super(UserProxyAdmin, self).__init__(model, admin_site)

class CarDetailsAdmin(admin.ModelAdmin):  
    list_filter = ('conflict_manually_resolved',('created_at', DateFieldListFilter),)
    list_editable = ('conflict_manually_resolved',)
    
    def __init__(self, model, admin_site):
        self.list_display = [field.name for field in model._meta.fields]
        super(CarDetailsAdmin, self).__init__(model, admin_site)

class ReportAdmin(admin.ModelAdmin):  
    list_filter = ('status', ('created_at', DateFieldListFilter),)
    list_editable = ("status", "resolution")
    def __init__(self, model, admin_site):
        self.list_display = [field.name for field in model._meta.fields]
        super(ReportAdmin, self).__init__(model, admin_site)

admin.site.register(Category, CategoryAdmin)
admin.site.register(City, CityAdmin)
admin.site.register(Car, CarAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(UserProxy, UserProxyAdmin)
admin.site.register(CarDetails, CarDetailsAdmin)
admin.site.register(Report, ReportAdmin)