from django.contrib import admin
from .models import SecurityToken


class SecurityTokenAdmin(admin.ModelAdmin):
    list_display = ("id", "creation_date", "code", "expiration_after_days")
    search_fields = list_display


admin.site.register(SecurityToken, SecurityTokenAdmin)
