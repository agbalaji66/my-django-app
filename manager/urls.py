from django.urls import path
from . import views

urlpatterns = [
    path('', views.core,name='core'),
    path('user_role/', views.user_role,name='user_role'),
    path('task_info/', views.task_info,name='task_info'),
    path('add_acc/', views.add_acc,name='add_acc'),
    path('edit/', views.edit,name='edit'),
    path('db_view/', views.db_view,name='db_view'),
    path('attendence/', views.attendence,name='attendence'),
    path('atten_log/', views.atten_log,name='atten_log'),
    path('mon_prod/', views.mon_prod,name='mon_prod'),
    path('mon_qual/', views.mon_qual,name='mon_qual'),
    path('produc/', views.produc,name='produc'),
    path('cost/', views.cost,name='cost'),
    path('qual_report/', views.qual_report,name='qual_report'),
    path('score_card/', views.score_card,name='score_card'),
]


