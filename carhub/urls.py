from django.urls import path
from django.urls.conf import include, re_path
from carhub import views

urlpatterns = [
    path('', views.Index, name = "index"),
    path('api/home', views.Home, name = "home"),

    path('api/user/<int:pk>', views.UserDashboard, name="user-dashboard"),
    path('api/user/<int:pk>/car-data', views.CarDataAPI, name="car-data"),
    path('api/user/<int:pk>/bank-detail', views.BankDetails, name="bank-detail"),
    path('api/user/<int:pk>/rider-order-detail', views.RiderOrderDetails, name="rider-order-detail"),
    path('api/user/<int:pk>/report-now', views.ReportNow, name="report-now"),

    path('api/media/<str:folder>/<str:file>', views.protected_media, name="protected_media"),

    path('api/signup', views.Signup, name = "signup"),
    path('api/activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('api/signin', views.Signin, name = "signin"),
    path('api/signout', views.Signout, name = "signout"),


    path('api/rentcar', views.RentCar, name = "rentcar"),

    path('api/ridecar', views.RideCar, name = "ridecar"),
    path('api/price-calculator', views.PriceCalculator, name = "pricecalculator"),
    path('api/ridecar/<int:city>', views.RideCar, name = "ridecar"),
    path('api/book/<int:carid>', views.Book, name = "bookcar"),
    path('api/order-status/',views.handlerequest, name="order-status/"),


    path('api/test',views.test),
    re_path(r'.*',views.view_404,name='404')
]
