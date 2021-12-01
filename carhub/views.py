import os
from backend import settings
from django.core.checks import messages
from django.http.response import FileResponse, HttpResponse, HttpResponseForbidden, HttpResponseNotFound, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMessage
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.db.models import Q
from django.utils import timezone

from carhub.models import *
from carhub.token import account_activation_token
from carhub.forms import *
from carhub.utils import CreationDataSaver

# ML Files
from carhub.utils import DrivingLicense, DrivingLicenseDataSaver


@csrf_exempt
def Home(request):
    city = list(City.objects.values())
    date = datetime.now()
    return JsonResponse(city, safe=False)

@csrf_exempt
def UserDashboard(request, pk):
    if request.user.id == pk or request.user.is_superuser:
        if request.method == "GET":
            userData = list(User.objects.filter(id = pk).values('username', 'first_name', 'last_name', 'email', 'userproxy__dl', 'userproxy__is_valid_renter', 'userproxy__is_valid_rider'))
            order = list(Order.objects.filter(userid__id = pk).order_by('bookingDate'))
            userData[0]['userproxy__dl'] = userData[0]['userproxy__dl'].url
            return JsonResponse({'user': userData, 'order':order}, status = 200)
        elif request.method == "POST":
            if request.FILES.get('file', None) is not None:
                try:
                    userproxy = UserProxy.objects.get(user = request.user)
                    userproxy.dl = request.FILES['file']
                    userproxy.is_valid_rider = False
                    userproxy = CreationDataSaver(userproxy)

                    # Checking Driving License and Name
                    userproxy.save() 
                    message = DrivingLicenseDataSaver(userproxy)        
                    userproxy.save() 
                    message = 'Updated' if not message else message
                except UserProxy.DoesNotExist:
                    userproxy = UserProxy(user = request.user, is_valid_renter = False, is_valid_rider = False, dl = request.FILES['file'])
                    userproxy = CreationDataSaver(userproxy)
                    message = DrivingLicenseDataSaver(userproxy)  
                    userproxy.save()
                    message = 'Uploaded' if not message else message
                return JsonResponse({'message':'DL {message}. We will review and get back to you'.format(message = message)}, status = 201)
            else:
                return JsonResponse({'message':'No File Uploaded'}, status = 400)
    else:
        return JsonResponse({'message': "Not authorized to access this page."}, status = 401)

@csrf_exempt
def Signin(request):
    if request.method == "POST":
        if request.user.is_authenticated:
            return JsonResponse({"login":"Already LoggedIn"})   # Change to be done
        email = request.POST.get('email', None)
        password = request.POST.get('password', None)

        try:
            username = User.objects.get(email = email).username
        except:
            return JsonResponse({'message': "Email Not Found."}, status = 401)
        user = authenticate(username = username, password = password)
        if user is not None:    
            login(request, user)
            return JsonResponse({"login":"successful", "userid":user.id, 'csrftoken': request.COOKIES.get('csrftoken'), 'sessionid': request.session.session_key})
        else:
            request.session['invalid_user'] = 1
            return JsonResponse({'message': "Not authorized to access this page."}, status = 401)
    return JsonResponse({'message': "Show SignIn Form."}, status = 200)

@csrf_exempt
def Signout(request):
    if request.user.is_authenticated:
        logout(request)
        return JsonResponse({'message': "Redirect to Home."}, status = 302)
    return JsonResponse({'message': "Not Logged In."}, status = 401)


@csrf_exempt
def Signup(request):
    if request.method == "POST":
        username = request.POST.get('username', None)
        email = request.POST.get('email', None)
        password = request.POST.get('password', None)
        if username and email and password:
            try:
                user = User.objects.filter(Q(email=email) | Q(username=username))[0]
                return JsonResponse({'message': "Already Exists."}, status = 403)
            except:
                user = User.objects.create_user(username=username, password= password, email=email)
                user.is_active = False
                user.save()
                current_site = get_current_site(request)
                mail_subject = 'Activate your Carhub account.'
                message = render_to_string('acc_active_email.html', {
                    'user': user,
                    'domain': current_site.domain,
                    'uid':urlsafe_base64_encode(force_bytes(user.pk)),
                    'token':account_activation_token.make_token(user),
                })
                to_email = email
                email = EmailMessage(
                            mail_subject, message, to=[to_email]
                )
                email.send()
                login(request, user)
                return JsonResponse({'Mail': "Sent"}, status = 201)
    return JsonResponse({'message': "Show SignUp Form."}, status = 200)

def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        return JsonResponse({'message':'Thank you for your email confirmation. Now you can login your account.'})
    else:
        return JsonResponse({'message':'Activation link is invalid!'})

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
                return JsonResponse({'message': "Already Exists."}, status = 403)
            except:
                form = RentCarForm(request.POST or None, request.FILES or None)
                print(form.errors)
                if form.is_valid():
                    car = form.save(commit=False)
                    car.user = request.user
                    car.created_by = 'User'
                    car.updated_by = 'User'
                    car.created_at = timezone.now()
                    car.updated_at = timezone.now()
                    car.save()
                    return JsonResponse({'message': "Added Car."}, status = 201)
        else:
            return JsonResponse({'message': "Redirect To SignIn."}, status = 302)
    else:
        context = {}
        context['city'] = list(City.objects.values('id', 'name'))
        context['category'] = list(Category.objects.values('id', 'name'))
        if request.user.is_authenticated:
            context['userdata'] = list(Car.objects.filter(user = request.user).values())
            for car in context['userdata']:
                car['photo'] = car['photo'].url
        return JsonResponse(context, status = 200)
        # return render(request, 'index.html')

def protected_media(request, folder, file):
    document=None
    if folder == 'rc':
        document = get_object_or_404(Car, rc=os.path.join(folder, file).replace("\\","/"))
        document.dl = None
    elif folder == 'dl':
        document = get_object_or_404(UserProxy, dl=os.path.join(folder, file).replace("\\","/"))
        document.rc = None
    else:
        return JsonResponse({'message': "Not Found."}, status = 404)
    if request.user == document.user or request.user.is_superuser :
        response = FileResponse(document.dl or document.rc)
        return response
    else:
        return JsonResponse({'message': "Not authorized to access this media."}, status = 401)

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
            car_notbooked = Car.objects.filter(city__id = city).exclude(car_detail__in=car_all).values('id', 'brand', 'modelName', 'year', 'category__name', 'price', 'user_id', 'city_id', 'photo', 'rc')
            car_notbooked_date = Car.objects.filter(city__id = city,  car_detail__orderDateFrom__lt=fromDate, car_detail__orderDateExpire__gt=toDate).values('id', 'brand', 'modelName', 'year', 'category__name', 'price', 'user_id', 'city_id', 'photo', 'rc')
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

def Book(request, carid):
    if request.user.is_authenticated:
        if request.method == 'GET':
            car = list(Car.objects.filter(id = carid).values())
            date_range_unavailable = list(Order.objects.filter(car__id = carid).values('orderDateFrom', 'orderDateExpire'))
            return JsonResponse({'data' : car, 'date_range_unavailable':date_range_unavailable})
        if request.method == 'POST':
            fromDate = request.POST.get('from')
            toDate = request.POST.get('to')
            # Take Date Input -- Done
            # Check DL(check validated user) At the time of signup check whether he has uploaded everything
            # Check Balance

            
            return 

def test(request):
    if request.user.is_authenticated:
        return JsonResponse({'success':True})
    else:
        return JsonResponse({'success':False})