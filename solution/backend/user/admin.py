from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from .models import DepartmentGroup, Division, Profile


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profiles'
    fields = ('department', 'department_group', 'division')
    readonly_fields = ('department', 'department_group', 'division')


class CustomUserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'department', 'division', 'department_group')
    list_select_related = ('profile',)

    def department(self, instance):
        return instance.profile.department

    def department_group(self, instance):
        return instance.profile.department_group.name if instance.profile.department_group else None

    def division(self, instance):
        return instance.profile.division.name if instance.profile.division else None

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return []
        return super().get_inline_instances(request, obj)


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
admin.site.register(Division)
admin.site.register(DepartmentGroup)
