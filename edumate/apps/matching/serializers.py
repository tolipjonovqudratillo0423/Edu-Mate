from rest_framework import serializers

from apps.matching.services import PartnerResult


class PartnerGoalSerializer(serializers.Serializer):
    current_level = serializers.IntegerField()
    target_level = serializers.IntegerField()
    current_score = serializers.DecimalField(max_digits=6, decimal_places=1, allow_null=True)
    target_score = serializers.DecimalField(max_digits=6, decimal_places=1, allow_null=True)
    deadline = serializers.DateField(allow_null=True)
    weekly_hours = serializers.IntegerField()


class PartnerAvailabilitySerializer(serializers.Serializer):
    id = serializers.IntegerField()
    weekday = serializers.IntegerField()
    slot = serializers.CharField()


class PartnerSerializer(serializers.Serializer):
    """
    Serializes a PartnerResult object for discovery.
    Response includes:
      - full_name, city, age_group
      - track and track_name
      - goal (current_level, target_level, current_score, target_score, deadline, weekly_hours)
      - availability (list of candidate slots)
      - score (matching score)
    """
    full_name = serializers.CharField()
    city = serializers.CharField()
    age_group = serializers.CharField()
    track = serializers.CharField()
    track_name = serializers.CharField()
    goal = PartnerGoalSerializer()
    availability = PartnerAvailabilitySerializer(many=True)
    score = serializers.IntegerField()

    def to_representation(self, instance: PartnerResult):
        goal = instance.goal
        user = goal.user
        profile = getattr(user, "profile", None)
        slots = getattr(user, "availability_slots", [])

        return {
            "full_name": profile.full_name if profile else "",
            "city": profile.city if profile else "",
            "age_group": profile.age_group if profile else "",
            "track": goal.track.name,
            "track_name": goal.track.name,
            "goal": {
                "current_level": goal.current_level,
                "target_level": goal.target_level,
                "current_score": goal.current_score,
                "target_score": goal.target_score,
                "deadline": goal.deadline,
                "weekly_hours": goal.weekly_hours,
            },
            "availability": [
                {
                    "id": slot.id,
                    "weekday": slot.weekday,
                    "slot": slot.slot,
                }
                for slot in slots
            ],
            "score": instance.score,
        }
