# from Carhub.carhub.views.checkout import MERCHANT_KEY
import json
import os
from carhub.models import Car, Order
from django.http.response import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from carhub.utils import CreationDataSaver
from PayTm import Checksum

MERCHANT_KEY=os.environ.get('MERCHANT_KEY')

@csrf_exempt
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
            fromDate = request.POST.get('from', None)
            toDate = request.POST.get('to', None)
            price = request.POST.get('price', None)
            print(fromDate, toDate, price)

            if not fromDate or not toDate:
                return JsonResponse({"message":"Invalid Dates"}, status = 422)

            car = Car.objects.get(id = carid)
            order = Order(userid = request.user, car = car, orderDateFrom = fromDate, orderDateExpire = toDate, totalOrderCost = price)
            order = CreationDataSaver(order)
            order.save()

            # PAYTM Check
            # Confirm status of payment otherwise payment will be Pending in Order Table
            param_dict = {

                'MID': os.environ.get('MID'),
                'ORDER_ID': str(order.id),
                'TXN_AMOUNT': str(price),
                'CUST_ID': request.user.email,
                'INDUSTRY_TYPE_ID': 'Retail',
                'WEBSITE': 'WEBSTAGING',
                'CHANNEL_ID': 'WEB',
                'CALLBACK_URL':'http://127.0.0.1:8000/order-status/',  #To be decided
            }
            param_dict['CHECKSUMHASH'] = Checksum.generate_checksum(param_dict, MERCHANT_KEY)
            return JsonResponse({"param_dict":param_dict})
            # return render(request, 'static/paytm.html', {'param_dict': param_dict})
    else:
        return JsonResponse({'message': 'Redirect To Sign in'}, status = 302)

csrf_exempt
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
        if response_dict['RESPCODE'] == '01':
            print('order successful')
            order = Order.objects.get(id = response_dict['ORDERID'])
            order.status='BOOKED'
            order.save()
            # for item in order:
            #     name=item.name
            #     emailId= item.email
            # template = render_to_string('shop/orderEmail.html',{'response_dict':response_dict,'name':name})
            # email= EmailMessage(
            #     'Order Confirmation',
            #     template,
            #     settings.EMAIL_HOST_USER,
            #     [emailId],
            # )
            # email.fail_silently = False
            # email.send()
            return JsonResponse({"message": "order succesful"},status=202)
        else:
            print('order was not successful because' + response_dict['RESPMSG'])
            # emailId=''
            return JsonResponse({"message": response_dict['RESPMSG']}, status=402)
    else:
        return JsonResponse(status=404)
    # return render(request, 'shop/paymentstatus.html', {'response': response_dict,'email':emailId})