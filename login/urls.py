from django.urls import path
from . import views

urlpatterns = [
    path('', views.homepage,name='homepage'),
    path('members/', views.members, name='members'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.logout_view, name='logout'),
]
