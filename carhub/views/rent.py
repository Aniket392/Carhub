from carhub.models import CarDetails, Car, UserProxy, City, Category
from carhub.forms import RentCarForm
from django.http.response import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
import joblib, pandas as pd, json
from carhub.utils import CreationDataSaver
from backend.settings import SCALER_PATH, ENCODER_PATH, MODEL_PATH

@csrf_exempt
def RentCar(request):   
    if request.method == "POST":
        if request.user.is_authenticated:
            brandname = request.POST.get('brand', None)
            model = request.POST.get('modelName', None)
            category = request.POST.get('category', None)
            year = request.POST.get('year', None)
            detaild_id = request.POST.get('detail_id', None)
            # account_no = request.POST.get('account_no', None)
            # ifsc = request.POST.get('ifsc', None)
            # holder_name = request.POST.get('holder_name', None)
            user = request.user
            try:
                details = CarDetails.objects.get(id = detaild_id)
                details.conflict_manually_resolved = False
                details.conflict = False
                details.save()
            except:
                return JsonResponse({"message":"No Details Found"}, status = 404)
            try:
                car = Car.objects.get(brand=brandname, modelName = model, user = user, year = year, category = category, details = details)
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
                    car.details = details
                    car.save()

                    # if account_no and ifsc and holder_name:
                    #     user_proxy = UserProxy.objects.get(user = request.user)
                    #     user_proxy.account_no = account_no
                    #     user_proxy.IFSC = ifsc
                    #     user_proxy.holder_name = holder_name
                    #     user_proxy.save()

                    return JsonResponse({'message': "Added Car."}, status = 201)
                else:
                    return JsonResponse({"message":form.errors})
        else:
            return JsonResponse({'message': "Redirect To SignIn."}, status = 302)
    else:
        context = {}
        context['city'] = list(City.objects.order_by('name').values('id', 'name'))
        context['category'] = list(Category.objects.order_by('name').values('id', 'name'))
        if request.user.is_authenticated:
            context['userdata'] = list(Car.objects.filter(user = request.user).values())

            # Checking Account Details
            has_account_details = False
            try:
                proxy = UserProxy.objects.get(user = request.user)
                if not proxy.account_no == None:
                    has_account_details = True
            except:
                return JsonResponse({"message":"No User Proxy"}, status = 422)
            context['has_account_details'] = has_account_details
            
            # Car Photo URL
            for car in context['userdata']:
                car['photo'] = car['photo'].url 
        return JsonResponse(context, status = 200)
        # return render(request, 'index.html')


@csrf_exempt
def PriceCalculator(request):

    if not request.user.is_authenticated:
        return JsonResponse({'message': 'Redirect To Sign in'}, status = 302)

    if request.method == "POST":
        #Loading Model
        scaler = joblib.load(open(SCALER_PATH, "rb"))
        labelencoder = joblib.load(open(ENCODER_PATH, "rb"))
        model = joblib.load(open(MODEL_PATH, "rb"))

        #Extracting from Form
        year = request.POST.get('year', None)
        manufacturer = request.POST.get('brand', None)
        odometer = request.POST.get('odometer', None)
        fuel = request.POST.get('fuel', None)
        drive = '4wd' if request.POST.get('drive', None) == 'true' else 'rwd' 
        cylinders = '4 cylinders'


        data = pd.DataFrame({'year':[year],
        'manufacturer':[manufacturer],
        'cylinders':[cylinders],
        'fuel':[fuel],
        'odometer':[odometer],
        'drive':[drive],
       })

       #Label Encoding
        for key in labelencoder:
            data[key] = labelencoder[key][data[key][0]]

        data = scaler.transform(data)
        price = model.predict(data)[0]

        percentage = 0.25
        dollar = 70

        price = round(((price*percentage*dollar)/100), 2)

        car_details = CarDetails(year = year, odometer = odometer, fuel = fuel, manufacturer = manufacturer, drive = drive, cylinders = cylinders, price_by_user = price, price_by_model = price, user = request.user)
        car_details = CreationDataSaver(car_details)
        car_details.save()
        return JsonResponse({"price":price, "detailid":car_details.id})
    
    elif request.method == 'PUT':
        data = json.loads(request.body.decode('utf8').replace("'", '"'))
        detailid = data.get('detailid', None)
        user_price = data.get('user_price', None)
        if user_price:
            try:
                detail = CarDetails.objects.get(id = detailid)
                detail.price_by_user = user_price
                detail.conflict = True
                detail.updated_at = timezone.now()
                detail.save()

                return JsonResponse({"message":"Updated the User Price. We will Manually Check the Rent Price For Car"}, status = 202)
            except:
                return JsonResponse({"message":"Invalid Detail ID"}, status = 422)
        else:
            return JsonResponse({"message":"No Conflict With Price"}, status = 302)

    else: 
        return JsonResponse({"message":"Invalid request"}, status=405)