from django.contrib import admin
from .models import MessageLog

@admin.register(MessageLog)
class MessageLogAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'channel', 'recipient', 'status', 'created_at']
    list_filter = ['channel', 'status']
    search_fields = ['recipient', 'user__username']
    readonly_fields = ['created_at', 'updated_at']
