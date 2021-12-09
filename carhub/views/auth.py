from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.db.models import Q
from django.http.response import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_text
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from carhub.token import account_activation_token


@csrf_exempt
def Signin(request):
    if request.method == "POST":
        email = request.POST.get('email', None)
        password = request.POST.get('password', None)

        try:
            username = User.objects.get(email = email).username
        except:
            return JsonResponse({'message': "Email Not Found."}, status = 401)
        user = authenticate(username = username, password = password)
        if user is not None:    
            if not user.is_active:
                return JsonResponse({"message":"Activate your account."})   # Change to be done
            login(request, user)
            return JsonResponse({"login":"successful", "userid":user.id, 'csrftoken': request.COOKIES.get('csrftoken'), 'sessionid': request.session.session_key,"is_active": user.is_active ,"is_valid_rider":user.userproxy.is_valid_rider})
        else:
            request.session['invalid_user'] = 1
            return JsonResponse({'message': "Not authorized to access this page."}, status = 401)
    return JsonResponse({'message': "Show SignIn Form."}, status = 302)

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
                print(email)
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