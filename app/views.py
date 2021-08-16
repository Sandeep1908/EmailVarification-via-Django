from django.http.response import HttpResponse
from Core.settings import EMAIL_HOST_USER
import uuid
from django.contrib.auth.models import User
from django.shortcuts import redirect, render
from .models import Profile
from django.contrib import messages
from django.core.mail import send_mail
from django.contrib.auth import authenticate,login,logout



def home(request):
    if request.user.is_authenticated:
        if request.session.get('username')==request.user.username:
            return render(request, 'app/home.html')
        else:
            return HttpResponse('plese login first')
    else:
        return redirect('/login')


def login_attemp(request):
    if not request.user.is_authenticated:
        if request.method=='POST':
            username=request.POST['username']
            password=request.POST['password']

            user=User.objects.filter(username=username).first()
            if user is None:
                messages.info(request,'User not found')
                return redirect('/login')
            
            profile=Profile.objects.filter(user=user).first()
            if not profile.is_valid:
                messages.info(request,'Your account is not varified please check you mail')
                return redirect('/login')
            
            reg=authenticate(username=username,password=password)
            if reg is None:
                messages.info(request,'Wrong password')
                return redirect('/login')
            else:            
                login(request,reg)
                request.session['username']=username
                return redirect('/')


        return render(request,'app/login.html')
    else:
        return redirect('/')


def register(request):
    if not request.user.is_authenticated:
        if request.method == 'POST':
            username = request.POST['username']
            email = request.POST['email']
            password = request.POST['password']

            if User.objects.filter(username=username).first():
                messages.info(request, 'Username is already  taken')
                return redirect('/register')

            if User.objects.filter(email=email).first():
                messages.info(request, 'Email is already Taken')
                return redirect('/register')

            user = User(username=username, email=email)
            user.set_password(password)
            if user is not None:
                user.save()

            token = str(uuid.uuid4())
            profile = Profile.objects.create(user=user, token=token)
            if profile is not None:
                profile.save()
            send_confirmation_mail(email,token)
            return redirect('/token/')

        return render(request, 'app/register.html')
    else:
        return redirect('/')
    
def logout_user(request):
    logout(request)
    return redirect('/login')

def verify(request,token):
    profile=Profile.objects.filter(token=token).first()
    if profile:
        if profile.is_valid:
            messages.info(request,'Your account is already varified')
            return redirect('/login')
        
        profile.is_valid=True
        profile.save()
        messages.info(request,'Your account has been varified')
        return redirect('/login')
    

def token_sent(request):
    return render(request,'app/token.html')


def send_confirmation_mail(email,token):
    subject=f'your account need to be verify'
    messages=f'please click this link to be varified http://127.0.0.1:8000/verify/{token}'
    email_from=EMAIL_HOST_USER
    recipient_list=[email]
    send_mail(subject,messages,email_from,recipient_list)