from rest_framework import serializers

from apps.goals.models import Goal


class GoalSerializer(serializers.ModelSerializer):
    """
    Used for both read and write.
    - `user` and `track_name` are read-only.
    - `track` is write-only on input (PrimaryKeyRelatedField).
    - Validation of cross-field rules (levels, deadline, weekly_hours)
      lives in GoalService; the serializer only validates field types/formats.
    """

    track_name = serializers.CharField(source="track.name", read_only=True)
    track_slug = serializers.CharField(source="track.slug", read_only=True)

    class Meta:
        model = Goal
        fields = [
            "id",
            "user",
            "track",
            "track_name",
            "track_slug",
            "current_level",
            "target_level",
            "current_score",
            "target_score",
            "deadline",
            "weekly_hours",
            "created_at",
            "updated_at",
        ]
        extra_kwargs = {
            "user": {"read_only": True},
            "created_at": {"read_only": True},
            "updated_at": {"read_only": True},
        }
