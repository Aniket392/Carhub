from django.contrib.auth.models import User
from django.http.response import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from carhub.models import Car, CarDetails, Order, Report, UserProxy
from carhub.utils import CreationDataSaver, DrivingLicenseDataSaver
import datetime

@csrf_exempt
def UserDashboard(request, pk):
    if request.user.id == pk or request.user.is_superuser:
        if request.method == "GET":
            userData = list(User.objects.filter(id = pk).values('username', 'first_name', 'last_name', 'email', 'userproxy__dl', 'userproxy__is_valid_renter', 'userproxy__is_valid_rider'))
            # order = list(Order.objects.filter(userid__id = pk).order_by('bookingDate').values())
            # CarDetails and Bank details
            return JsonResponse({'user': userData}, status = 200)
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
def CarDataAPI(request,pk):
    if not (request.user.id == pk or request.user.is_superuser):
        return JsonResponse({"message":"Not authorized to access this page."}, status=401)
    if request.method == 'GET':
        car_data = list(CarDetails.objects.filter(user=pk).values('year', 'odometer', 'fuel', 'manufacturer', 'drive', 'cylinders', 'price_by_model', 'price_by_user', 'conflict', 'conflict_manually_resolved', 'user', 'car__photo', 'car__modelName'))
        for data in car_data:
            if data['car__photo']:
                data['car__photo'] = data['car__photo'].url        
        order_of_users_car = list(Order.objects.filter(car__user__id=pk).order_by('-bookingDate').values())
        return JsonResponse({"car_data":car_data,"order_of_users_car":order_of_users_car})
    if request.method == 'POST':
        orderid = request.POST.get('orderid', None)
        try:
            order = Order.objects.get(id = orderid)
        except:
            return JsonResponse({"message":"No Order with this ID."},status = 404)
        order.status = 'COM'
        expected_return_date = order.orderDateExpire.date()         # Expected Return Date
        return_date = datetime.datetime.now().date()                # Return Date
        day_difference = (return_date - expected_return_date).days
        if day_difference <= 0:
            day_difference = 0
        outstanding_amount = day_difference*order.car.details.price_by_model         # Outstanding Amount
        # Mail send by AKhsit
        order.save()
        return JsonResponse({"expected_return_date":expected_return_date, "return_date":return_date, "outstanding_amount":outstanding_amount})


@csrf_exempt
def BankDetails(request, pk):
    if not (request.user.id == pk or request.user.is_superuser):
        return JsonResponse({"message":"Not authorized to access this page."}, status=401)
    if request.method == 'GET':
        bank_details = list(UserProxy.objects.filter(user = pk).values('id', 'account_no', 'IFSC', 'holder_name'))
        return JsonResponse({'bank_details':bank_details}, status=200)
    elif request.method == 'POST':
        account_no = request.POST.get('account_no', None)
        IFSC = request.POST.get('IFSC', None)
        holder_name = request.POST.get('holder_name', None)

        if account_no and IFSC and holder_name:
            try:
                userproxy = UserProxy.objects.get(user = pk)
                userproxy.account_no = account_no
                userproxy.IFSC = IFSC
                userproxy.holder_name = holder_name
                userproxy.save()
            except UserProxy.DoesNotExist:
                user = User.objects.get(id=pk)
                userproxy = UserProxy(user = user, is_valid_renter = False, is_valid_rider = False, account_no=account_no, IFSC=IFSC, holder_name=holder_name)
                userproxy = CreationDataSaver(userproxy)
                userproxy.save()
            return JsonResponse({"message":"Bank Details Saved."})
        else:
            return JsonResponse({"message":"Invalid Form Data"}, status=400)
    return JsonResponse({"message":"Invalid Request"}, status=405)

@csrf_exempt
def RiderOrderDetails(request, pk):
    if not (request.user.id == pk or request.user.is_superuser):
        return JsonResponse({"message":"Not authorized to access this page."}, status=401)
    if request.method == 'GET':
        order = list(Order.objects.filter(userid=pk).order_by('-bookingDate').values('id', 'status', 'car__brand', 'car__modelName', 'car__year', 'car__user__first_name', 'car__photo', 'bookingDate', 'orderDateFrom', 'orderDateExpire', 'totalOrderCost', 'status'))

        for ord in order:
            ord['car__photo'] = ord['car__photo'].url
        
        return JsonResponse({"rider_order":order}, status=200)
    if request.method == 'POST':
        orderid = request.POST.get('orderid', None)
        try:
            order = Order.objects.get(id = orderid)
            order.status = 'RSRE'
            order.updated_at = datetime.datetime.now()
            order.save()
        except Exception as e:
            return JsonResponse({"message":"No Order with this ID"}, status = 404)
        return JsonResponse({"message":"Ride Ended from your side. Waiting for Confirmation from Renter."})



@csrf_exempt
def ReportNow(request, pk):
    if not (request.user.id == pk or request.user.is_superuser):
        return JsonResponse({"message":"Not authorized to access this page."}, status=401)
    if request.method == 'GET':
        report = list(Report.objects.filter(user__id = pk).values())
        return JsonResponse({"reports": report})
    if request.method == 'POST':
        message = request.POST.get('message', None)
        orderid = request.POST.get('orderid', None)
        try:
            order = Order.objects.get(id = orderid)
        except:
            return JsonResponse({"message":"No Order with this ID."})
        try:
            report = Report.objects.get(order__id = orderid, user = request.user.id)
        except :
            report = Report(user = request.user, order = order, issueDate = datetime.date.today(), message = message, status = 'OPEN')
            report = CreationDataSaver(report)
        if report.status != 'CLOSE':
            report.save()
            # Mail Sending
            return JsonResponse({"message":"Report recorded", "reportid":report.id})
        else:
            return JsonResponse({"message":"Report Already recorded and is In-Progress."})
        
