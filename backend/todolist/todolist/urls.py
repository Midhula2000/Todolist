"""
URL configuration for todolist project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import path
from todo import views

urlpatterns = [
    path('signup',views.Signup),
    path('login',views.login),
    path('addtask',views.addtask),
    path('gettask',views.gettasks),
    path('searchtask',views.search_tasks),
    path('filtertask',views.filter_tasks),
    path('completetask', views.complete_task),
   path('edittask', views.edit_task),  
    path('deletetask', views.delete_task),
   path('importtasks', views.import_tasks),
    path('exporttasks/', views.export_tasks),
   
   
]
