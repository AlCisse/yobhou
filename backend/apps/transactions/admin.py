from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html
from .models import Transaction


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['reference_number', 'user', 'amount', 'payment_method', 'status_badge', 'aml_flag', 'created_at']
    list_filter = ['status', 'payment_method', 'aml_reviewed', 'created_at']
    search_fields = ['reference_number', 'user__username', 'user__phone_number']
    readonly_fields = ['aml_alerts_display', 'created_at', 'updated_at']
    ordering = ['-created_at']
    actions = ['mark_as_reviewed', 'export_for_audit']
    
    def status_badge(self, obj):
        colors = {
            'pending': '#FFC107',
            'completed': '#28A745',
            'failed': '#DC3545',
            'flagged': '#FD7E14',
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px; font-weight: bold;">{}</span>',
            colors.get(obj.status, '#6C757D'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Statut'
    
    def aml_flag(self, obj):
        if obj.aml_alerts:
            severity_counts = {}
            for alert in obj.aml_alerts:
                sev = alert.get('severity', 'UNKNOWN')
                severity_counts[sev] = severity_counts.get(sev, 0) + 1
            
            badges = []
            for sev, count in severity_counts.items():
                color = {'CRITICAL': '#DC3545', 'HIGH': '#FD7E14', 'MEDIUM': '#FFC107', 'LOW': '#28A745'}.get(sev, '#6C757D')
                badges.append(f'<span style="background-color: {color}; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px;">{sev}: {count}</span>')
            return format_html(' '.join(badges))
        return format_html('<span style="color: #28A745;">✓ Clean</span>')
    aml_flag.short_description = 'AML'
    
    def aml_alerts_display(self, obj):
        if not obj.aml_alerts:
            return 'Aucune alerte AML'
        
        html = '<ul style="margin: 10px 0; padding-left: 20px;">'
        for alert in obj.aml_alerts:
            html += f'<li><strong>{alert["type"]}</strong> ({alert["severity"]}): {alert["description"]}</li>'
        html += '</ul>'
        return format_html(html)
    aml_alerts_display.short_description = 'Alertes AML'
    
    def mark_as_reviewed(self, request, queryset):
        updated = queryset.update(
            aml_reviewed=True,
            aml_reviewed_by=request.user,
            aml_reviewed_at=timezone.now()
        )
        self.message_user(request, f'{updated} transactions marquées comme revues')
    mark_as_reviewed.short_description = 'Marquer comme revu (AML)'
    
    def export_for_audit(self, request, queryset):
        # Export CSV pour audit BCEAO
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="yobhou_audit_export.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Reference', 'User', 'Amount', 'Payment Method', 'Status', 'AML Alerts', 'Created At'])
        
        for tx in queryset:
            writer.writerow([
                tx.reference_number,
                tx.user.username,
                str(tx.amount),
                tx.payment_method,
                tx.status,
                str(tx.aml_alerts),
                tx.created_at.isoformat()
            ])
        
        return response
    export_for_audit.short_description = 'Export CSV pour audit'

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('user', 'meter_reading')
