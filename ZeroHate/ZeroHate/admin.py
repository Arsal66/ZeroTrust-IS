from django.contrib import admin
from .models import ClassificationResult, User, LoginOTP


admin.site.register(ClassificationResult)
admin.site.register(User)
admin.site.register(LoginOTP)