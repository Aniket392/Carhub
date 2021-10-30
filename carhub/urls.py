from django.urls import path
from django.urls.conf import include, re_path
from carhub import views

urlpatterns = [
    path('', views.Home, name = ""),

    path('user/<int:pk>', views.UserDashboard, name="user-dashboard"),

    path('media/cars/<str:file>', views.protected_media, name="protected_media"),
    path('signup', views.Signup, name = "signup"),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('signin', views.Signin, name = "signin"),
    path('signout', views.Signout, name = "signout"),


    path('rentcar', views.RentCar, name = "rentcar"),

    path('ridecar', views.RideCar, name = "ridecar"),
    path('ridecar/<int:city>', views.RideCar, name = "ridecar"),
    path('book/<int:carid>', views.Book, name = "bookcar"),
    path('test',views.test)
]
