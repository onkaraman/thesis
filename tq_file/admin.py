from django.contrib import admin
from .models import TQFile


class TQFileAdmin(admin.ModelAdmin):
    list_display = ("id", "creation_date", "archived", "project", "display_file_name")
    search_fields = list_display

admin.site.register(TQFile, TQFileAdmin)