# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from datetime import datetime, time
from django.utils import timezone
from .models import *

global login_user
# Create your views here.
def homepage(request):
    return render(request,'welcome.html',{})

def members(request):
    return render(request,'members.html',{})

def logout_view(request):
    d = dict()
    d["status"] = "You have been logged out."
    logout(request)
    return render(request, 'logout.html', d)

def check_login():
    if datetime.now().time() >= time(6,0) and datetime.now().time() <= time(10,30):
        return "Work from Office"
    elif datetime.now().time() >= time(10,31) and datetime.now().time() <= time(12,0):
        return "Late Login"
    elif datetime.now().time() >= time(17,0) and datetime.now().time() <= time(5,59):
        return "NightOWL"   
    else:
        return "Half Day" 

def user_login(request):
    template = 'login_form.html'
    if request.POST:
        rda =[]
        mnger = []
        auditor = []

        lead_obj = role.objects.all().filter(user_role='lead')
        for i in lead_obj:
            rda.append(i.user_name.strip())
        
        man_obj = role.objects.all().filter(user_role='manager')
        for i in man_obj:
            mnger.append(i.user_name.strip())
        
        auditor_obj = role.objects.all().filter(user_role='auditor')
        for i in auditor_obj:
            auditor.append(i.user_name.strip())
        
        
        username=str(request.POST.get('username'))
        password =str(request.POST.get('password'))
        login_user = username
        user = authenticate(username=username, password=password)

        if user is not None:
            if user.is_active:
                date_today = datetime.today().strftime('%Y-%m-%d')
                check_loggedin = Login.objects.all().filter(user=username,login_time__contains=date_today)
                #check whether user logged in today or not
                if check_loggedin:
                    login(request, user)
                    if username in mnger:
                        return redirect('../core')
                    elif username in auditor:
                        return redirect('../auditor')
                    elif username in rda:
                        return redirect('../core')
                #if user has not logged in today
                else:
                    if str(request.POST.get('login_status')) == 'Work from Office':
                            status = check_login()
                            if status == "NightOWL":
                                print("Do Nothing")
                            elif status == "Half Day":
                                login_log = Login.objects.create(user=username,login_status=status,login_time=datetime.now(),benchmark_hours=int(4))
                                login_log.save()
                            else:
                                login_log = Login.objects.create(user=username,login_status=status,login_time=datetime.now(),benchmark_hours=int(8))
                                login_log.save()
                    else:
                        login_log = Login.objects.create(user=username,login_status=str(request.POST.get('login_status')),login_time=datetime.now(),benchmark_hours=int(8))
                        login_log.save()

                    login(request, user)
                    if username in mnger:
                        return redirect('../core')
                    elif username in auditor:
                        return redirect('../auditor')
                    elif username in rda:
                        return redirect('../core')
                    else:
                        return HttpResponse("<h1>You are not a authorized person! If so ask you manager to add to group.</h1>")
        else:
            return HttpResponse("<h1>Failed logged in</h1>")
    return render(request,template,{})
















