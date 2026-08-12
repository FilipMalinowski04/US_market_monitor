from django.contrib import admin

from .models import WatchedCompany


@admin.register(WatchedCompany)
class WatchedCompanyAdmin(admin.ModelAdmin):
    list_display = ("ticker", "name", "country", "sector", "added_at")
    search_fields = ("ticker", "name")
    ordering = ("-added_at",)
