from carhub.models import Car
from django.http.response import JsonResponse
from django.views.decorators.csrf import csrf_exempt


def Book(request, carid):
    if request.user.is_authenticated:
        if not request.user.is_active or  not request.user.userproxy.is_valid_rider:
            return JsonResponse({"message":"Either ID not activated or DL not Uploaded"})

        if request.method == 'GET':
            try:
                car = Car.objects.filter(id=1).select_related('details', 'user', 'city', 'category')
                context = vars(car[0])
            except:
                return JsonResponse({"message":"No such Car Found"}, status = 404)
            context['photo'] = car[0].photo.url
            context['price'] = car[0].details.price_by_model
            context['category_id'] = car[0].category.name
            context['user_id'] = car[0].user.first_name
            context['city_id'] = car[0].city.name

            context.pop('_state')
            car = list(Car.objects.filter(id = carid).values())
            # date_range_unavailable = list(Order.objects.filter(car__id = carid).values('orderDateFrom', 'orderDateExpire'))
            # return JsonResponse({'data' : context, 'date_range_unavailable':date_range_unavailable})
            return JsonResponse(context)
        if request.method == 'POST':
            fromDate = request.POST.get('from')
            toDate = request.POST.get('to')
            # Take Date Input -- Done
            # Check DL(check validated user) At the time of signup check whether he has uploaded everything
            # Check Balance
    else:
        return JsonResponse({'message': 'Redirect To Sign in'}, status = 302)