from carhub.models import City
from datetime import datetime
from django.http.response import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def Home(request):
    city = list(City.objects.values())
    date = datetime.now()
    return JsonResponse(city, safe=False)