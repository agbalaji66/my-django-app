import pandas as pd
import numpy as np
import xlsxwriter 
try:
    from io import BytesIO as IO # for modern python
except ImportError:
    from io import StringIO as IO # for legacy python
from django.shortcuts import render
from django.http import HttpResponse
from login.models import *
from auditor.models import *
from django.db.models import Avg, Count, Min, Sum
from datetime import date, datetime, timedelta, time
import calendar


Month = ['January','Feburary','March','April','May','June','July','August','September','October','November','December']
sm_Mon = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sept','Oct','Nov','Dec']

def get_aud():
    aas = []
    xy = role.objects.all().filter(user_role="auditor")
    for i in xy:
        aas.append(i.user_name)
    return aas

def get_task():
    tt = []
    xy = task_information.objects.all()
    for j in xy:
        tt.append(j.Sub_Task)
    return tt
# Create your views here.
def core(request):
    current_user = request.user
    user= current_user.username
    return render(request,'manager.html',{'user':user})

def user_role(request):
    current_user = request.user
    user= current_user.username

    obj = role.objects.all().order_by('user_role')
    context = {'user':user,'obj': obj}

    if request.POST:
        if str(request.POST.get('form_type'))=='del':
            ob = role.objects.filter(user_name=str(request.POST.get('uname')),user_role=str(request.POST.get('urole'))).delete()
        else:
            user = role.objects.create(user_name=str(request.POST.get('user')),user_role=str(request.POST.get('role')))
            user.save()
        return render(request,'user_role.html',context)
    return render(request,'user_role.html',context)

def task_info(request):
    current_user = request.user
    user= current_user.username

    obj = task_information.objects.all()
    if request.POST:
        if str(request.POST.get('form_type'))=='del':
            ob = task_information.objects.filter(Task_ID=str(request.POST.get('id'))).delete()
        else:
            task = task_information.objects.create(Task=str(request.POST.get('task')),Sub_Task=str(request.POST.get('sub')),volume=str(request.POST.get('vol')),benchmark=str(request.POST.get('ben')))
            task.save()
        return render(request,'task.html',{'obj':obj})
    return render(request,'task.html',{'obj':obj})

def add_acc(request):
    current_user = request.user
    user= current_user.username
    
    qs = DataLog.objects.all().filter(accuracy__isnull=True).exclude(task="Adhoc")
    
    mon = request.GET.get('mon')
    ass = request.GET.get('ass')

    if mon and mon != 'Choose...':
        qs = qs.filter(month=mon)

    if ass and ass != 'Choose...':
        qs = qs.filter(associate=ass)
    
    if request.POST:
        ob = DataLog.objects.get(UUID=str(request.POST.get('id')))
        ob.accuracy = str(request.POST.get('acc'))
        ob.aoa_comments = str(request.POST.get('com'))
        ob.aoa_by = str(user)
        ob.save()
        return render(request,'accuracy.html',{'qs':qs,'aas':get_aud(),'Mon':Month})
    return render(request,'accuracy.html',{'qs':qs,'aas':get_aud(),'Mon':Month})

def edit(request):
    current_user = request.user
    user= current_user.username
    
    qs = DataLog.objects.all().filter(Productivity__isnull=False)

    mon = request.GET.get('mon')
    ass = request.GET.get('ass')
    tk = request.GET.get('tk')

    if mon and mon != 'Choose...':
        qs = qs.filter(month=mon)

    if ass and ass != 'Choose...':
        qs = qs.filter(associate=ass)

    if tk and tk != 'Choose...':
        qs = qs.filter(Sub_Task=tk)

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
        else:
            voo = DataLog.objects.get(UUID=str(request.POST.get('id')))
            voo.hours_spent = str(request.POST.get('hr'))
            voo.Productivity = float(request.POST.get('hr'))*60
            voo.save()
        return render(request,'edit.html',{'qs':qs.exclude(volume=0),'qs1':qs.filter(volume=0,task="Adhoc"),'qs2':qs.filter(volume=0,task="BPM"),'aas':get_aud(),'Mon':Month,'task':get_task()})
        
    return render(request,'edit.html',{'qs':qs.exclude(volume=0),'qs1':qs.filter(volume=0,task="Adhoc"),'qs2':qs.filter(volume=0,task="BPM"),'aas':get_aud(),'Mon':Month,'task':get_task()})

def db_view(request):
    qs = DataLog.objects.all()

    mon = request.GET.get('mon')
    ass = request.GET.get('ass')
    tk = request.GET.get('tk')

    if mon and mon != 'Choose...':
        qs = qs.filter(month=mon)

    if ass and ass != 'Choose...':
        qs = qs.filter(associate=ass)

    if tk and tk != 'Choose...':
        qs = qs.filter(Sub_Task=tk)

    if request.POST:
        if str(request.POST.get('form_type'))=="del":
            ob = role.objects.filter(UUID=str(request.POST.get('id'))).delete()
            return render(request,'dbv.html',{'qs':qs,'aas':get_aud(),'Mon':Month,'task':get_task()})
        else:
            df_output = pd.DataFrame(list(qs.values())) 
            excel_file = IO()
            xlwriter = pd.ExcelWriter(excel_file, engine='xlsxwriter')
            df_output.to_excel(xlwriter, 'sheetname')

            xlwriter.save()
            xlwriter.close()
            excel_file.seek(0)
            response = HttpResponse(excel_file.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = 'attachment; filename=myfile.xlsx'
            return response

    return render(request,'dbv.html',{'qs':qs,'aas':get_aud(),'Mon':Month,'task':get_task()})

def attendence(request):
    template = 'attendence.html'
    attendence_list = []
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
    attendence_list=create_attendence(date_range)
    context = {'attendence_list':attendence_list,'date_range':print_date_range,'day':day}

    if request.POST:
        start_date=request.POST.get('startDate')
        start_date= datetime.strptime(start_date,'%Y-%m-%d')
        end_date=request.POST.get('endDate')
        end_date= datetime.strptime(end_date,'%Y-%m-%d')
        
        delta = timedelta(days=1)
        date_range = []
        print_date_range = []
        day = []
        while start_date <= end_date:
            dd = calendar.day_name[start_date.weekday()]
            day.append(dd[:3])
            date_range.append(start_date.strftime("%Y-%m-%d"))
            print_date_range.append(start_date.strftime("%d-%b"))   
            start_date += delta

        attendence_list=[]
        attendence_list=create_attendence(date_range)
        
        context = {'attendence_list':attendence_list,'date_range':print_date_range,'day':day}
    return render(request,template,context)

def create_attendence(date_range):
    user = []
    obj = role.objects.all()
    for i in obj:
        user.append(i.user_name.strip())
    user.sort()
    attendence_list = []
    for u in user:
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

def atten_log(request):
    usr = []
    obj = role.objects.all()
    for i in obj:
        usr.append(i.user_name.strip())
    usr.sort()
    midday = datetime.strptime('11:00:00', '%H:%M:%S')
    midday = datetime.time(midday)

    qs = Login.objects.all()

    rda = request.GET.get('rda')
    etadate_min = request.GET.get('date_min')
    etadate_max = request.GET.get('date_max')

    if rda and rda != 'Choose...':
        qs = qs.filter(user=rda)
    if etadate_min:
        qs = qs.filter(login_time__gte=etadate_min)

    if etadate_max:
        qs = qs.filter(login_time__lte=etadate_max)

    if request.POST:
        if str(request.POST.get('form_type'))=='add':
            if str(request.POST.get('action'))=="Work from Home" or str(request.POST.get('action'))=="Work from Office":
                obj= Login.objects.create(user=str(request.POST.get('ass')),login_status=str(request.POST.get('action')),login_time=datetime.combine(datetime.strptime(str(request.POST.get('date')), '%Y-%m-%d'),midday),benchmark_hours=int(8))
                obj.save()
            else:
                obj= Login.objects.create(user=str(request.POST.get('ass')),login_status=str(request.POST.get('action')),login_time=datetime.combine(datetime.strptime(str(request.POST.get('date')), '%Y-%m-%d'),midday),benchmark_hours=int(4))
                obj.save()
        else:
            ob = Login.objects.filter(id=str(request.POST.get('id'))).delete()
        print_ob = qs.all().order_by("-login_time")[:20]
        return render(request,'log_attendence.html',{'qs':print_ob,'RDA':usr})
    print_ob = qs.all().order_by("-login_time")[:20]
    return render(request,'log_attendence.html',{'qs':print_ob,'RDA':usr})

def mon_prod(request):
    mon  = [1,2,3,4,5,6,7,8,9,10,11,12]
    obj = role.objects.all().exclude(user_role='manager')
    users = []
    for i in obj:
        users.append(i.user_name)
    users.sort()
    
    ben = []
    for r in users:
        u = []
        u.append(r)
        for i in mon:   
            benchmark_ob = Login.objects.all().filter(user=r,login_time__month=i).aggregate(Sum('benchmark_hours'))
            bench = benchmark_ob.get('benchmark_hours__sum')
            # u.append(bench)
            prod_ob = DataLog.objects.all().filter(associate=r,performed_date__month=i).aggregate(Sum('Productivity'))
            prod = prod_ob.get('Productivity__sum')
            if bench==None or prod==None:
                percent = 0
            else:
                percent = (prod/(bench*60))*100
            u.append(round(percent,2))
        ben.append(u)
    return render(request,'month.html',{'ben':ben,'MONTH':Month})

def mon_qual(request):
    mon  = [1,2,3,4,5,6,7,8,9,10,11,12]
    obj = role.objects.all().exclude(user_role='manager')
    users = []
    for i in obj:
        users.append(i.user_name)
    users.sort()
    
    ben = []
    for r in users:
        u = []
        u.append(r)
        for i in mon:   
            prod_ob = DataLog.objects.all().filter(associate=r,performed_date__month=i).aggregate(Avg('accuracy'))
            prod = prod_ob.get('accuracy__avg')
            if prod==None:
                percent = 0
            else:
                percent = prod
            u.append(round(percent,2))
        ben.append(u)
    return render(request,'quality.html',{'ben':ben,'MONTH':Month})

def produc(request):
    template = 'productivity_auditor.html'
    auditor_list = get_aud()
    yesterday_date = datetime.strftime(datetime.now() - timedelta(1), '%Y-%m-%d')
    date_range = [yesterday_date]

    prod = []
    for associate in auditor_list:
        u = []
        productvty = DataLog.objects.filter(associate=associate,performed_date__contains=yesterday_date).aggregate(Sum('Productivity'))
        productvty = productvty.get('Productivity__sum')
        if productvty is None:
            prod_value = 0
        else:
            prod_value = int(productvty)/60
        u = [associate]
        #benchmark hours
        ben_ob = Login.objects.all().filter(user=associate,login_time__contains=yesterday_date).count()
        if ben_ob == 0:
            benchmark = 0
            u.append('L')
            u.append('L')
        else:
            ob=Login.objects.get(user=associate,login_time__contains=yesterday_date)
            benchmark = int(ob.benchmark_hours)
            percent = prod_value/benchmark
            u.append(round(percent*100,2))
            u.append(round(percent*100,2))
        prod.append(u)
    context2 = {'prod' : prod , 'date_range' : date_range }
    
    if request.POST:
        start_date=request.POST.get('startDate')
        start_date= datetime.strptime(start_date,'%Y-%m-%d')
        end_date=request.POST.get('endDate')
        end_date= datetime.strptime(end_date,'%Y-%m-%d')
        
        delta = timedelta(days=1)
        date_range = []
        print_date_range =[]
        while start_date <= end_date:
            #print (start_date.strftime("%Y-%m-%d"))
            date_range.append(start_date.strftime("%Y-%m-%d"))
            print_date_range.append(start_date.strftime("%d-%b")) 
            start_date += delta
        prod_user = []
        for associate in auditor_list:
            u=[]
            tp,tb =0,0
            u.append(associate)
            for dd in date_range:
                productvty = DataLog.objects.filter(associate=associate,performed_date__contains=dd).aggregate(Sum('Productivity'))
                productvty = productvty.get('Productivity__sum')
                if productvty is None:
                    prod_value = 0
                else:
                    prod_value = int(productvty)/60
                    tp+=int(productvty)
                #benchmark hours
                ben_ob = Login.objects.all().filter(user=associate,login_time__contains=dd).count()
                if ben_ob == 0:
                    benchmark = 0
                    u.append('L')
                else:
                    ob=Login.objects.get(user=associate,login_time__contains=dd)
                    benchmark = int(ob.benchmark_hours)
                    tb+=int(ob.benchmark_hours)
                    percent = prod_value/benchmark
                    percent = int(percent*100)
                    u.append(str(percent)+"%")
            if tb == 0:
                u.append('<font color="blue"><b>'+"0%"+'</b></font>')
            else:
                tot = tp/(tb*60)
                u.append('<font color="blue"><b>'+str(int(tot*100))+"%"+'</b></font>')
            prod_user.append(u)
        
        context1={'prod':prod_user,'date_range':print_date_range}
        return render(request,template,context1)
    return render(request,template,context2)

def create_cost(yesterday_date):
    tk = []
    ob = task_information.objects.all()
    for i in ob:
        tk.append(i.Sub_Task)
    auditor = get_aud()
    master_list=[]
    for j in tk:
        u=[]
        # tt=0
        u.append('<b>'+str(j)+'</b>')
        for i in auditor:
            productvty = DataLog.objects.filter(associate=i,performed_date__contains=yesterday_date,Sub_Task=j).aggregate(Sum('Productivity'))
            productvty = productvty.get('Productivity__sum')
            if productvty is None:
                u.append(0)
            else:
                u.append(round(int(productvty)/60,2))
                # tt+=int(productvty)

        # productvty = DataLog.objects.filter(associate=i,performed_date__contains=yesterday_date,task="Adhoc").aggregate(Sum('Productivity'))
        # productvty = productvty.get('Productivity__sum')
        # if productvty is None:
        #     u.append(0)
        # else:
        #     u.append(round(int(productvty)/60,2))
        #     tt+=int(productvty)        
        # u.append(round(tt/60,2))
        master_list.append(u)

    return master_list

def qual_report(request):
    qs = DataLog.objects.all().filter(accuracy__isnull=False)

    mon = request.GET.get('mon')
    ass = request.GET.get('ass')
    tk = request.GET.get('tk')

    if mon and mon != 'Choose...':
        qs = qs.filter(month=mon)

    if ass and ass != 'Choose...':
        qs = qs.filter(associate=ass)

    if tk and tk != 'Choose...':
        qs = qs.filter(Sub_Task=tk)
        
    if request.POST:
        ob = DataLog.objects.get(UUID=str(request.POST.get('id')))
        ob.accuracy = str(request.POST.get('acc'))
        ob.save()
    return render(request,'qual_edit.html',{'qs':qs,'aas':get_aud(),'Mon':Month,'task':get_task()})

def score_card(request):
    mon  = [1,2,3,4,5,6,7,8,9,10,11,12]
    obj = role.objects.all().exclude(user_role='manager')
    users = []
    for i in obj:
        users.append(i.user_name)
    users.sort()

    ben = []
    for r in users:
        u = []
        u.append(r)
        for i in mon:   
            benchmark_ob = Login.objects.all().filter(user=r,login_time__month=i).aggregate(Sum('benchmark_hours'))
            bench = benchmark_ob.get('benchmark_hours__sum')
            # u.append(bench)
            prod_ob = DataLog.objects.all().filter(associate=r,performed_date__month=i).aggregate(Sum('Productivity'))
            prod = prod_ob.get('Productivity__sum')
            if bench==None or prod==None:
                percent = 0
            else:
                percent = (prod/(bench*60))*100
            u.append("<b><font color='blue'>"+str(round(percent,2))+"</font></b>")
  
            qual_ob = DataLog.objects.all().filter(associate=r,performed_date__month=i).aggregate(Avg('accuracy'))
            qual = qual_ob.get('accuracy__avg')
            if qual==None:
                percent = 0
            else:
                percent = qual
            u.append("<b><font color='green'>"+str(round(percent,2))+"</font></b>")
        ben.append(u)

    return render(request,'score_card.html',{'ben':ben,'MONTH':sm_Mon})

def last_week():
    today = datetime.today()
    weekday = today.weekday()
    start_delta = timedelta(days=weekday,weeks=1)
    start_of_week = today-start_delta
    week_dates=[]
    for day in range(7):
        week_dates.append(start_of_week+timedelta(days=day))
    return week_dates

#capacity planner
def cost(request):
    template = 'daily_cost.html'
    today_date = datetime.now()

    dd_week = last_week()
    start = dd_week[0]
    end = dd_week[6]
    hc,cap,uti = calculate_cap(start,end)
    
    
    if request.POST:
        if str(request.POST.get('form-type'))=="last_week":
            start_date=request.POST.get('startDate')
            start= datetime.strptime(start_date,'%Y-%m-%d')
            end_date=request.POST.get('startDate')
            end= datetime.strptime(start_date,'%Y-%m-%d')
        elif str(request.POST.get('form-type'))=="this_month":
            end = datetime.today()
            start = end.replace(day=1)
        elif str(request.POST.get('form-type'))=="last_month":
            end = datetime.today().replace(day=1)-timedelta(days=1)
            start = end.replace(day=1)

        hc,cap,uti = calculate_cap(start,end)
        context = {'hc':hc,'cap':cap,'uti':uti,'start':start,'end':end}
        return render(request,template,context)

    context = {'hc':hc,'cap':cap,'uti':uti,'today_date':today_date,'start':start,'end':end}
    return render(request,template,context)

def calculate_cap(start,end):
    head_count = Login.objects.filter(login_time__gte=start,login_time__lte=end).values('user').distinct().count()
    date1 = pd.to_datetime(start,format="%d-%m-%Y").date()
    date2 = pd.to_datetime(end,format="%d-%m-%Y").date()
    working_days = np.busday_count( date1 , date2)
    
    tot_ob = Login.objects.filter(login_time__gte=start,login_time__lte=end).aggregate(Sum('benchmark_hours'))
    tot = tot_ob.get('benchmark_hours__sum')
    if tot is None:
        tot = 0
    else:
        tot = int(tot)
    
    if (int(tot)/(working_days*head_count*8)) == 0:
        capacity = 0
    else:
        capacity = int(tot)/(working_days*head_count*8)
    
    productvty = DataLog.objects.filter(performed_date__gte=start,performed_date__lte=end).aggregate(Sum('Productivity'))
    productvty = productvty.get('Productivity__sum')
    if productvty is None:
        productvty = 0
    else:
        productvty = int(productvty)

    if tot==0:
        utilization=0
    else:
        utilization = int(productvty)/int(tot)*60
    return head_count,capacity,utilization



























