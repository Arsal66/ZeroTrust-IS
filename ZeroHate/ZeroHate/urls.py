"""
URL configuration for ZeroHate project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),

    path("dashboard", views.dashboard, name="dashboard"),
    path('signup/', views.signup_view, name='signup'),
    path('confirmation_sent/', views.confirmation_sent, name='confirmation_sent'),  # Email confirmation sent page
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),  # Activation link handling
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('classify-text/', views.classify_text_view, name='classify_text'),
    path('verify_otp/', views.verify_otp, name='verify_otp'),
    path('upload_file/', views.upload_file, name='upload_file'),
]
