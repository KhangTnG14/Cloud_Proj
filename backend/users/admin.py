
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, SystemLog

@admin.register(SystemLog)
class SystemLogAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'user', 'action', 'ip_address')
    list_filter = ('action', 'created_at')
    readonly_fields = ('created_at',)

# Hiển thị thêm các trường phone, role trong trang Admin 
class CustomUserAdmin(UserAdmin):
    model = User
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('phone', 'role')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('phone', 'role')}),
    )

admin.site.register(User, CustomUserAdmin)