from django.contrib import admin
from .models import UserProfile


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "creation_date", "user", "token")
    search_fields = list_display


admin.site.register(UserProfile, UserProfileAdmin)
