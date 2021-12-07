from carhub.models import Car, Order, City
from django.http.response import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from datetime import timedelta


@csrf_exempt
def RideCar(request, city=None):
    if request.user.is_authenticated:
        fromDate = request.GET.get('fromDate', '')
        toDate = request.GET.get('toDate', '')
        if fromDate == '':
            fromDate = timezone.now()
        if toDate == '':
            toDate = timezone.now()+timedelta(days=1)
        if city is not None:
            car_all = Order.objects.filter(car__city__id = city)
            car_notbooked = Car.objects.filter(city__id = city).exclude(car_detail__in=car_all).values('id', 'brand', 'modelName', 'year', 'category__name', 'details__price_by_model', 'user_id', 'city_id', 'photo', 'rc')
            car_notbooked_date = Car.objects.filter(city__id = city,  car_detail__orderDateFrom__lt=fromDate, car_detail__orderDateExpire__gt=toDate).values('id', 'brand', 'modelName', 'year', 'category__name', 'details__price_by_model', 'user_id', 'city_id', 'photo', 'rc')
            car_data = list(car_notbooked | car_notbooked_date)

            # For Taking out URL from object
            for car in car_data:
                car['photo'] = car['photo'].url
                car['rc'] = car['rc'].url

            return JsonResponse({'data': car_data})
        else:
            city_data = list(City.objects.values('id', 'name'))
            return JsonResponse({'data': city_data})
    else:
        return JsonResponse({'message': 'Redirect To Sign in'}, status = 302)