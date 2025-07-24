from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.admin_login, name='admin_login'),
    # path('userreport',views.user_report, name='user_report'),

]