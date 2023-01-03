from django.urls import path
from . import views

urlpatterns = [
    path('', views.auditor,name='auditor'),
    path('create_log/', views.create_log,name='create_log'),
    path('my_log/', views.my_log,name='my_log'),
    path('my_quality/', views.my_quality,name='my_quality'),
    path('my_atten/', views.my_atten,name='my_atten'),
    path('score/', views.score,name='score'),
]
