"""nstv_fe URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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
from django.contrib import admin
from django.urls import path

from nstv import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index),
    path('shows_index/', views.shows_index, name='shows_index'),
    path('shows/<int:show_id>', views.show_index),
    path('shows/<int:show_id>/episode/<int:eid>/download', views.download_episode),
    path('add_show/', views.add_show_page),
]