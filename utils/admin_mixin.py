from django.contrib import admin


class DateListFilterMixin:
    list_filter = ('is_active', ('created_at', admin.DateFieldListFilter), ('updated_at', admin.DateFieldListFilter))


class ActionsMixin:
    def activate_objects(self, request, queryset):
        queryset.update(is_active=True)

    def deactivate_objects(self, request, queryset):
        queryset.update(is_active=False)

    activate_objects.short_description = "Activate selected objects"
    deactivate_objects.short_description = "Deactivate selected objects"
