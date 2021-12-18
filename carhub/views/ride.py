from django.db.models import Q
from django.db.models.aggregates import Count
from carhub.models import Car, Category, Order, City
from django.http.response import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from datetime import timedelta

@csrf_exempt
def RideCar(request, city=None):
    if request.user.is_authenticated:
        fromDate = request.GET.get('fromDate', '')
        toDate = request.GET.get('toDate', '')
        category = request.GET.get('category', [])


        if fromDate == '':
            fromDate = timezone.now()+timedelta(days=1)
        if toDate == '':
            toDate = timezone.now()+timedelta(days=2)
        if city is not None:
            car_all = Order.objects.filter(car__city__id = city)

            car_notbooked = Car.objects.filter(city__id = city).exclude(car_detail__in=car_all).annotate(no_of_order=Count('car_detail__id', filter = Q(car_detail__status = 'COM'))).values('id', 'brand', 'modelName', 'year', 'category__name', 'details__price_by_model', 'user_id', 'city_id', 'photo', 'no_of_order')
            car_notbooked_date = Car.objects.filter(Q(city_id=city) & (Q(car_detail__orderDateFrom__gt=toDate) | Q(car_detail__orderDateExpire__lt=fromDate))).distinct().annotate(no_of_order=Count('car_detail__id', filter = Q(car_detail__status = 'COM'))).values('id', 'brand', 'modelName', 'year', 'category__name', 'details__price_by_model', 'user_id', 'city_id', 'photo', 'no_of_order')
        
            for cat in category:
                car_notbooked = car_notbooked.filter(category = cat)        # Category filter
                car_notbooked_date = car_notbooked_date.filter(category=cat)
            
            car_data = list(car_notbooked.union(car_notbooked_date))

            # For Taking out URL from object
            for car in car_data:
                car['photo'] = car['photo'].url
            
            cat_data = list(Category.objects.values('id', 'name'))

            return JsonResponse({'data': car_data, 'category':cat_data})
        else:
            city_data = list(City.objects.order_by('name').values('id', 'name'))
            return JsonResponse({'data': city_data})
    else:
        return JsonResponse({'message': 'Redirect To Sign in'}, status = 302)

