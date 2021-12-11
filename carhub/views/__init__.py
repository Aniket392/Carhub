from carhub.views.auth import Signin, Signout, Signup, activate
from carhub.views.book import Book, handlerequest
from carhub.views.dashboard import UserDashboard, CarDataAPI, BankDetails, RiderOrderDetails, ReportNow
from carhub.views.home import Home
from carhub.views.media import protected_media
from carhub.views.rent import RentCar, PriceCalculator
from carhub.views.ride import RideCar

from django.http.response import JsonResponse

def test(request):
    if request.user.is_authenticated:
        return JsonResponse({'success':True})
    else:
        return JsonResponse({'success':False})