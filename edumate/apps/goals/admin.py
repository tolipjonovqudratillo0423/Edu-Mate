from django.contrib import admin

from apps.goals.models import (
    Track,
    Goal,
    Availability
)


@admin.register(Track)
class  TrackAdmin(admin.ModelAdmin):
    
    list_display = (
        "name",
        "category",
        "is_active"
    )
    list_editable = [
        "is_active"
    ]
    search_fields = (
        "name",
    )


@admin.register(Goal)
class GoalAdmin(admin.ModelAdmin):
    list_display = (
        "get_user_email",
        "get_track_name",
        "current_score",
        "current_level",
        "target_level",
    )
    
    @admin.display(ordering="user__email", description="Email")
    def get_user_email(self, obj):
        return obj.user.email if obj.user.email else "-"
    
    @admin.display(ordering="track__name", description="Track")
    def get_track_name(self, obj):
        return obj.track.name if obj.track.name else "-"
    
    


@admin.register(Availability)
class AvailabilityAdmin(admin.ModelAdmin):
    list_display = (
        "get_uaer_email",
        "weekday",
        "slot",
    )
    @admin.display(ordering="user__email", description="Email")
    def get_uaer_email(self, obj):
        return obj.user.email if obj.user.email else "-"
    
    