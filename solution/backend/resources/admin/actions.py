from django.contrib import admin


@admin.action(description="Mark selected as approved")
def mark_approved(modeladmin, request, queryset):
    queryset.update(approved=True)


@admin.action(description="Mark selected as not approved")
def mark_not_approved(modeladmin, request, queryset):
    queryset.update(approved=False)
