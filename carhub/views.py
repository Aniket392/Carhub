from django.core.checks import messages
from django.http.response import FileResponse, HttpResponse, HttpResponseForbidden, HttpResponseNotFound, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from carhub.models import *
from carhub.forms import *
from django.utils import timezone
import os
from backend import settings
from django.contrib.auth.decorators import login_required

# Create your views here.
@csrf_exempt
def Home(request):
    city = list(City.objects.values())
    date = datetime.now()
    return JsonResponse(city, safe=False)

def UserDashboard(request, pk):
    if request.user.id == pk or request.user.is_superuser:
        return HttpResponse("pk")
    else:
        return HttpResponseForbidden('Not authorized to access this page.')

@csrf_exempt
def Signin(request):
    if request.method == "POST":
        if request.user.is_authenticated:
            return JsonResponse({"login":"Already LoggedIn"})
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username = username, password = password)
        if user is not None:    
            login(request, user)
            # return redirect("/")
            return JsonResponse({"login":"successful"})
            # return redirect('base')
        else:
            request.session['invalid_user'] = 1
    return HttpResponse('Show signin form')

@csrf_exempt
def Signout(request):
    if request.user.is_authenticated:
        logout(request)
        return redirect("/")
    return HttpResponse("Not logged in")


@csrf_exempt
def Signup(request):
    if request.method == "POST":
        username = request.POST['username']
        email = request.POST['password']
        password = request.POST['password']

        try:
            user = User.objects.get(email=email)
            return HttpResponse("Already Exists")
        except:
            user = User.objects.create_user(username=username, password= password, email=email)
            user.save()
            login(request, user)
            return HttpResponse("Created User")
    return HttpResponse('Show sign Up form')

@csrf_exempt
def RentCar(request):   
    if request.method == "POST":
        if request.user.is_authenticated:
            brandname = request.POST['brand']
            model = request.POST['modelName']
            category = request.POST['category']
            year = request.POST['year']
            price = request.POST['price']
            user = request.user

            try:
                car = Car.objects.get(brand=brandname, modelName = model, user = user, year = year, category = category, price=price)
                return HttpResponse("Already Exists")
            except:
                form = RentCarForm(request.POST or None, request.FILES or None)
                if form.is_valid():
                    car = form.save(commit=False)
                    car.user = request.user
                    car.created_by = 'User'
                    car.updated_by = 'User'
                    car.created_at = timezone.now()
                    car.updated_at = timezone.now()
                    car.save()
                    return HttpResponse("Added Car")
        else:
            return redirect('/signin')
    else:
        return render(request, 'index.html')

def protected_media(request, file):
    document = get_object_or_404(Car, photo="cars/"+ file)
    if request.user == document.user or request.user.is_superuser :
        path, file_name = os.path.split(file)
        response = FileResponse(document.photo)
        return response
    else:
        return HttpResponseForbidden('Not authorized to access this media.')

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
            car_notbooked = Car.objects.filter(city__id = city).exclude(car_detail__in=car_all).values()
            car_notbooked_date = Car.objects.filter(city__id = city,  car_detail__orderDateFrom__lt=fromDate, car_detail__orderDateExpire__gt=toDate).values()
            car_data = list(car_notbooked | car_notbooked_date)
            return JsonResponse({'data': car_data})
        else:
            city_data = list(City.objects.values('name'))
            return JsonResponse({'data': city_data})
    else:
        return redirect('/signin')

def Book(request, carid):
    if request.user.is_authenticated:
        if request.method == 'GET':
            car = list(Car.objects.filter(id = carid).values())
            date_range_unavailable = list(Order.objects.filter(car__id = carid).values('orderDateFrom', 'orderDateExpire'))
            return JsonResponse({'data' : car, 'date_range_unavailable':date_range_unavailable})
        if request.method == 'POST':
            fromDate = request.POST.get('from')
            toDate = request.POST.get('to')
            # Take Date Input
            # Check DL(check validated user) At the time of signup check whether he has uploaded everything
            # Check Balance

            
            return 