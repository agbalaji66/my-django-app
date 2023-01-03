import pandas as pd
import numpy as np
import xlsxwriter 
try:
    from io import BytesIO as IO # for modern python
except ImportError:
    from io import StringIO as IO # for legacy python
from django.shortcuts import render
from django.http import HttpResponse
from django.db.models import Avg, Count, Min, Sum
from datetime import date, datetime, timedelta
import calendar
from .models import *
from login.models import *

Month = ['January','Feburary','March','April','May','June','July','August','September','October','November','December']
# Create your views here.
def auditor(request):
    current_user = request.user
    user= current_user.username
    return render(request,'auditor_home.html',{'user':user})

def create_log(request):
    current_user = request.user
    user= current_user.username
    currentMonth = datetime.now().strftime('%B')
    bpm_obj = DataLog.objects.all().filter(status="WIP",associate=user).exclude(task="Adhoc")
    adh_obj = DataLog.objects.all().filter(task="Adhoc",status="WIP",associate=user)
    if request.POST:
        if str(request.POST.get('form_type'))=="Assigned":
            ob = DataLog.objects.create(associate=user,performed_date=str(request.POST.get('perform-date')),task=str(request.POST.get('task')),Sub_Task=str(request.POST.get('Subtask')))
            ob.status = "WIP"
            ob.date = datetime.today()
            ob.month = currentMonth
            ob.save()
            return render(request,'log.html',{'user':user,'bpm_obj':bpm_obj,'adh_obj':adh_obj})
        elif str(request.POST.get('form_type'))=="BPM":
            voo = DataLog.objects.get(UUID=str(request.POST.get('id')))
            ts = task_information.objects.get(Task=voo.task,Sub_Task=voo.Sub_Task)
            vlme = ts.volume
            tm = ts.benchmark
            if vlme == 0:
                voo.volume = 0
                voo.hours_spent = tm
                voo.filename = str(request.POST.get('fil'))
                voo.Productivity = float(tm)*60
                voo.status = "Completed"
                voo.save()
                return render(request,'log.html',{'user':user,'bpm_obj':bpm_obj,'adh_obj':adh_obj})
            else:
                voo.volume = str(request.POST.get('vol'))
                voo.hours_spent = int(request.POST.get('vol'))/int(vlme)*8
                voo.filename = str(request.POST.get('fil'))
                voo.Productivity = (int(request.POST.get('vol'))/int(vlme)*8)*60
                voo.status = "Completed"
                voo.save()
                return render(request,'log.html',{'user':user,'bpm_obj':bpm_obj,'adh_obj':adh_obj})
        else:
            ob = DataLog.objects.get(UUID=str(request.POST.get('id')))
            ob.filename = str(request.POST.get('com'))
            ob.hours_spent = str(request.POST.get('hr'))
            ob.volume = 0
            ob.Productivity = float(request.POST.get('hr'))*60
            ob.status = "Completed"
            ob.save()
            return render(request,'log.html',{'user':user,'bpm_obj':bpm_obj,'adh_obj':adh_obj})
    return render(request,'log.html',{'user':user,'bpm_obj':bpm_obj,'adh_obj':adh_obj})

def my_log(request):
    current_user = request.user
    user= current_user.username
    qs = DataLog.objects.all().filter(associate=user,status="Completed")

    mon = request.GET.get('mon')
    if mon and mon != 'Choose...':
        qs = qs.filter(month=mon)

    if request.POST:
        if str(request.POST.get('form_type'))=="volume":
            voo = DataLog.objects.get(UUID=str(request.POST.get('id')))
            ts = task_information.objects.get(Task=voo.task,Sub_Task=voo.Sub_Task)
            vlme = ts.volume
            voo.volume = str(request.POST.get('vol'))
            voo.hours_spent = int(request.POST.get('vol'))/int(vlme)*8
            voo.Productivity = (int(request.POST.get('vol'))/int(vlme)*8)*60
            voo.save()
            return render(request,'my_log.html',{'Mon':Month,'qs':qs.exclude(volume=0),'qs1':qs.filter(volume=0)})
        elif str(request.POST.get('form_type'))=="export":
            df_output = pd.DataFrame(list(qs.values())) 
            excel_file = IO()
            xlwriter = pd.ExcelWriter(excel_file, engine='xlsxwriter')
            df_output.to_excel(xlwriter, 'Data')
            xlwriter.save()
            xlwriter.close()
            excel_file.seek(0)
            response = HttpResponse(excel_file.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = 'attachment; filename=myfile.xlsx'
            return response
        else:
            voo = DataLog.objects.get(UUID=str(request.POST.get('id')))
            voo.hours_spent = str(request.POST.get('hr'))
            voo.Productivity = float(request.POST.get('hr'))*60
            voo.save()
            return render(request,'my_log.html',{'Mon':Month,'qs':qs.exclude(volume=0),'qs1':qs.filter(volume=0,task="Adhoc"),'qs2':qs.filter(volume=0,task="BPM")})
    return render(request,'my_log.html',{'Mon':Month,'qs':qs.exclude(volume=0),'qs1':qs.filter(volume=0,task="Adhoc"),'qs2':qs.filter(volume=0,task="BPM")})

def my_quality(request):
    current_user = request.user
    user= current_user.username
    qs = DataLog.objects.all().filter(associate=user,accuracy__isnull=False)

    mon = request.GET.get('mon')
    if mon and mon != 'Choose...':
        qs = qs.filter(month=mon)

    return render(request,'my_qual.html',{'Mon':Month,'qs':qs})

def my_atten(request):
    current_user = request.user
    u = current_user.username
   
    date_range = []
    print_date_range = []
    day = []

    start_date=datetime.today()
    start_date = start_date.replace(day=1)
    end_date=datetime.today()
   
    delta = timedelta(days=1)
    
    while start_date <= end_date:
        dd = calendar.day_name[start_date.weekday()]
        day.append(dd[:3])
        date_range.append(start_date.strftime("%Y-%m-%d"))
        print_date_range.append(start_date.strftime("%d-%b"))   
        start_date += delta

        if request.POST:
            start_date=request.POST.get('startDate')
            start_date= datetime.strptime(start_date,'%Y-%m-%d')
            end_date=request.POST.get('endDate')
            end_date= datetime.strptime(end_date,'%Y-%m-%d')
            date_range1 = []
            print_date_range = []
            day = []
            while start_date <= end_date:
                dd = calendar.day_name[start_date.weekday()]
                day.append(dd[:3])
                date_range1.append(start_date.strftime("%Y-%m-%d"))
                print_date_range.append(start_date.strftime("%d-%b"))   
                start_date += delta
            context1 = {'role':role,'user':u,'attendence_list':create_attendence(u,date_range1),'date_range':print_date_range,'day':day}
            return render(request,'atten_audit.html',context1)
            
    context = {'user':u,'attendence_list':create_attendence(u,date_range),'date_range':print_date_range,'day':day}
    return render(request,'atten_audit.html',context)

def create_attendence(u,date_range): 
    attendence_list = []
    a=[]
    tem=[]
    p,l,wfh = 0,0,0
    for dd in date_range:
        atten_obj = Login.objects.all().filter(user=u,login_time__contains=dd)
        if atten_obj.count() == 0:
            dt = datetime.strptime(dd,'%Y-%m-%d')
            holiday = calendar.day_name[dt.weekday()]
            if holiday[:3]=='Sat' or holiday[:3]=='Sun':
                status = '<font color="green">'+"WO"+'</font>'
            else:
                status = '<font color="red">'+"L"+'</font>'
                p+=1
        elif atten_obj.count() == 1:
            ob = Login.objects.get(user=u,login_time__contains=dd)
            status=ob.login_status
            if status == "Half Day":
                l +=1
                status = "HD"
            elif status == "Work from Office":
                status = "P"
            elif status == "Work from Home":
                status = "WFH" 
                wfh+=1
            else:
                l+=1 
                status = "LL"
        else:
            obj = Login.objects.all().filter(user=u,login_time__contains=dd)
            ob = obj[0]
            status=ob.login_status
            if status == "Half Day":
                l +=1
                status = "HD"
            elif status == "Work from Office":
                status = "P"
            elif status == "Work from Home":
                status = "WFH" 
                wfh+=1
            else:
                l+=1 
                status = "LL"
        a.append(status)
    tem = [u,p,l,wfh]
    for i in a:
        tem.append(i)
    attendence_list.append(tem)
    return attendence_list

def score(request):
    current_user = request.user
    user= current_user.username
    mon  = [1,2,3,4,5,6,7,8,9,10,11,12]
    
    p=[]
    q=[]
    p.append('<b>'+str("Productivity")+'</b>')
    q.append('<b>'+str("Quality")+'</b>')

    for i in mon:
        benchmark_ob = Login.objects.all().filter(user=user,login_time__month=i).aggregate(Sum('benchmark_hours'))
        bench = benchmark_ob.get('benchmark_hours__sum')
        prod_ob = DataLog.objects.all().filter(associate=user,performed_date__month=i).aggregate(Sum('Productivity'))
        prod = prod_ob.get('Productivity__sum')
        if bench==None or prod==None:
            percent = 0
        else:
            percent = (prod/(bench*60))*100
        p.append(round(percent,2))

        qua_ob = DataLog.objects.all().filter(associate=user,performed_date__month=i).aggregate(Avg('accuracy'))
        qua = qua_ob.get('accuracy__avg')
        if qua==None:
            quality = 0
        else:
            quality = qua
        q.append((quality))

    return render(request,'score.html',{'user':user,'prod':p,'qual':q,'mon':Month})

































