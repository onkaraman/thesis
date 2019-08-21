from django.contrib import admin
from .models import Project


class ProjectAdmin(admin.ModelAdmin):
    list_display = ("id", "creation_date", "user_profile", "name")
    search_fields = list_display

admin.site.register(Project, ProjectAdmin)
