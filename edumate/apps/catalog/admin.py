from django.contrib import admin

from apps.catalog.models import Track

@admin.register(Track)
class TrackAdmin(admin.ModelAdmin):
    
    list_display = (
        "name",
        "slug",
        "category",
        "is_active"
    )
    list_editable = [
        "is_active"
    ]
    search_fields = (
        "name",
        "slug"
    )