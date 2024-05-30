from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from .models import DepartmentDivision, DepartmentGroup, Profile


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profiles'
    fields = ('department', 'department_group', 'department_division')
    readonly_fields = ('department', 'department_group', 'department_division')


class CustomUserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)
    list_display = ('username',
                    'email',
                    'first_name',
                    'last_name',
                    'get_department',
                    'get_department_group',
                    'get_department_division')

    list_select_related = ('profile',)

    def get_department(self, instance):
        return instance.profile.department

    get_department.short_description = 'Department'

    def get_department_group(self, instance):
        return instance.profile.department_group

    get_department_group.short_description = 'Group'

    def get_department_division(self, instance):
        return instance.profile.department_division

    get_department_division.short_description = 'Division'

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return []
        return super().get_inline_instances(request, obj)


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
admin.site.register(DepartmentDivision)
admin.site.register(DepartmentGroup)
