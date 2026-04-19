from django.contrib import admin
from .models import MeterReading


@admin.register(MeterReading)
class MeterReadingAdmin(admin.ModelAdmin):
    list_display = ['user', 'meter_number', 'current_index', 'consumption', 'is_validated', 'created_at']
    list_filter = ['is_validated', 'created_at']
    search_fields = ['meter_number', 'user__username', 'user__phone_number']
    readonly_fields = ['ocr_data', 'created_at', 'updated_at']
    ordering = ['-created_at']

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('user')
