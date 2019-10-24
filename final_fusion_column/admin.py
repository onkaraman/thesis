from django.contrib import admin
from .models import FinalFusionColumn


class FFCAdmin(admin.ModelAdmin):
    list_display = ("id", "creation_date", "archived", "final_fusion", "source_tq", "source_column_name")
    search_fields = list_display


admin.site.register(FinalFusionColumn, FFCAdmin)
