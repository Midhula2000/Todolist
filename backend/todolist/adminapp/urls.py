from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.admin_login, name='admin_login'),
    path('user-report/',views.user_report, name='user_report'),
    path('user-usage-report/', views.user_usage_report, name='user_usage_report'),
]