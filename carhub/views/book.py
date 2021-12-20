# from Carhub.carhub.views.checkout import MERCHANT_KEY
import json
import os

from django.contrib.auth.models import User
from django.shortcuts import render
from carhub.models import Car, Order
from django.http.response import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from carhub.utils import CreationDataSaver
from PayTm import Checksum
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.contrib.sites.shortcuts import get_current_site
MERCHANT_KEY=os.environ.get('MERCHANT_KEY')

@csrf_exempt
def Book(request, carid):
    if request.user.is_authenticated:
        if not request.user.is_active or  not request.user.userproxy.is_valid_rider:
            return JsonResponse({"message":"Either ID not activated or DL not Uploaded"})

        if request.method == 'GET':
            try:
                car = Car.objects.filter(id=carid).select_related('details', 'user', 'city', 'category')
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
            fromDate = request.POST.get('from', None)
            toDate = request.POST.get('to', None)
            price = request.POST.get('price', None)
            print(fromDate, toDate, price)

            if not fromDate or not toDate:
                return JsonResponse({"message":"Invalid Dates"}, status = 422)

            car = Car.objects.get(id = carid)
            print(request.user.id)
            order = Order(userid = request.user, car = car, orderDateFrom = fromDate, orderDateExpire = toDate, totalOrderCost = price)
            order = CreationDataSaver(order)
            order.save()

            # PAYTM Check
            # Confirm status of payment otherwise payment will be Pending in Order Table
            domain = get_current_site(request).domain
            param_dict = {

                'MID': os.environ.get('MID'),
                'ORDER_ID': str(order.id),
                'TXN_AMOUNT': str(price),
                'CUST_ID': request.user.email,
                'INDUSTRY_TYPE_ID': 'Retail',
                'WEBSITE': 'WEBSTAGING',
                'CHANNEL_ID': 'WEB',
                'CALLBACK_URL':'http://' + domain + '/api/order-status/',  #To be decided
            }
            param_dict['CHECKSUMHASH'] = Checksum.generate_checksum(param_dict, MERCHANT_KEY)
            return JsonResponse({"param_dict":param_dict})
            # return render(request, 'static/paytm.html', {'param_dict': param_dict})
    else:
        return JsonResponse({'message': 'Redirect To Sign in'}, status = 302)

@csrf_exempt
def handlerequest(request):
    # paytm will send you post request here
    
    form = request.POST
    response_dict = {}
    for i in form.keys():
        response_dict[i] = form[i]
        if i == 'CHECKSUMHASH':
            checksum = form[i]

    verify = Checksum.verify_checksum(response_dict, MERCHANT_KEY, checksum)
    if verify:
        order = Order.objects.select_related('userid').get(id = response_dict['ORDERID'])
        name = order.userid.first_name
        to_email = order.userid.email
        if response_dict['RESPCODE'] == '01':
            
            renter_contact_number = order.car.user.userproxy.mobile_number
            order.status='BKD'
            order.save()

            # Mail to Rider
            mail_subject = 'Ride booked on successful payment'
            message = render_to_string('orderEmail.html', {
                'response_dict': response_dict,
                'name': name,
                'contact_number': renter_contact_number
            })
            email = EmailMessage(
                        mail_subject, message, to=[to_email]
            )
            email.fail_silently = False
            email.send()

            # Mail to renter
            car_name = " ".join([order.car.brand, order.car.modelName])
            date_of_booking = order.bookingDate.date()
            journey_start_date = order.orderDateFrom.date()
            journey_end_date = order.orderDateExpire.date()
            contact_number_rider = order.userid.userproxy.mobile_number
            name_of_rider = order.userid.first_name
            price = order.totalOrderCost
            renter_email = order.car.user.email
            renter_name = order.car.user.first_name

            car_details = {
                        "order_id": order.id,
                        "name": renter_name,
                        "car_name": car_name,
                        "booking_date": date_of_booking,
                        "journey_start_date": journey_start_date,
                        "journey_end_date": journey_end_date,
                        "contact_number_rider": contact_number_rider,
                        "name_of_rider": name_of_rider,
                        "price": price
            }
            mail_subject = 'Your car is booked'
            message = render_to_string('renterOrderEmail.html', car_details)
            email = EmailMessage(
                        mail_subject, message, to=[renter_email]
            )
            print(renter_email,mail_subject,message)
            email.fail_silently = False
            email.send()

        else:
            print('order was not successful because' + response_dict['RESPMSG'])
            
            order.status='FAIL'
            order.save()
            mail_subject = 'Booking failed '
            message = render_to_string('orderEmail.html', {
                'response_dict': response_dict,
                'name': name
            })
            email = EmailMessage(
                        mail_subject, message, to=[to_email]
            )
            email.send()
            # return JsonResponse({"message": response_dict['RESPMSG']}, status=402)
        return render(request, 'build/index.html')
    else:
        return JsonResponse(status=404)
    # return render(request, 'shop/paymentstatus.html', {'response': response_dict,'email':emailId})