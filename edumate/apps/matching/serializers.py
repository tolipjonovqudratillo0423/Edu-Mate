from rest_framework import serializers

from apps.catalog.models import Track
from apps.matching.models import Match, MatchRequest
from apps.matching.services import PartnerResult
from apps.users.models import User


# ------------------------------------------------------------------ #
# Partners Discovery Serializers                                     #
# ------------------------------------------------------------------ #

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
    id = serializers.IntegerField(source="goal.user.id", read_only=True)
    user_id = serializers.IntegerField(source="goal.user.id", read_only=True)
    full_name = serializers.CharField()
    city = serializers.CharField()
    age_group = serializers.CharField()
    track = serializers.CharField()
    track_name = serializers.CharField()
    track_id = serializers.IntegerField(source="goal.track.id", read_only=True)
    goal = PartnerGoalSerializer()
    availability = PartnerAvailabilitySerializer(many=True)
    score = serializers.IntegerField()

    def to_representation(self, instance: PartnerResult):
        goal = instance.goal
        user = goal.user
        profile = getattr(user, "profile", None)
        slots = getattr(user, "availability_slots", [])

        return {
            "id": user.id,
            "user_id": user.id,
            "full_name": profile.full_name if profile else "",
            "city": profile.city if profile else "",
            "age_group": profile.age_group if profile else "",
            "track": goal.track.name,
            "track_name": goal.track.name,
            "track_id": goal.track.id,
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


# ------------------------------------------------------------------ #
# MatchRequest Serializers                                           #
# ------------------------------------------------------------------ #

class MatchRequestCreateSerializer(serializers.Serializer):
    """
    Input serializer for creating a match request.
    from_user is set from request.user in the view/service.
    """
    to_user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    track = serializers.PrimaryKeyRelatedField(queryset=Track.objects.all())
    message = serializers.CharField(max_length=200, required=False, allow_blank=True)


class MatchRequestUpdateSerializer(serializers.Serializer):
    """
    Input serializer for updating a match request status.
    """
    status = serializers.ChoiceField(choices=MatchRequest.Status.choices)


class MatchRequestSerializer(serializers.ModelSerializer):
    """
    Output serializer for MatchRequest.
    """
    from_user_name = serializers.SerializerMethodField()
    to_user_name = serializers.SerializerMethodField()
    track_name = serializers.CharField(source="track.name", read_only=True)
    partner_user_id = serializers.SerializerMethodField()
    telegram_username = serializers.SerializerMethodField()

    def get_from_user_name(self, obj):
        profile = getattr(obj.from_user, "profile", None)
        return profile.full_name if profile else ""

    def get_to_user_name(self, obj):
        profile = getattr(obj.to_user, "profile", None)
        return profile.full_name if profile else ""

    def get_partner_user_id(self, obj):
        request = self.context.get("request")
        other = obj.to_user if request and request.user == obj.from_user else obj.from_user
        return other.id

    def get_telegram_username(self, obj):
        request = self.context.get("request")
        other = obj.to_user if request and request.user == obj.from_user else obj.from_user
        return other.telegram_username or ""

    class Meta:
        model = MatchRequest
        fields = [
            "id",
            "from_user",
            "from_user_name",
            "to_user",
            "to_user_name",
            "track",
            "track_name",
            "message",
            "status",
            "responded_at",
            "created_at",
            "updated_at",
            "partner_user_id",
            "telegram_username",
        ]
        read_only_fields = fields


# ------------------------------------------------------------------ #
# Mates Serializers                                                  #
# ------------------------------------------------------------------ #

class MateSerializer(serializers.ModelSerializer):
    """
    Output serializer for active/ended Match.
    Each item contains the other user's info:
      - full_name, city
      - track and track_name
      - status
      - created_date and created_at
    """
    full_name = serializers.SerializerMethodField()
    city = serializers.SerializerMethodField()
    partner_id = serializers.SerializerMethodField()
    partner_user_id = serializers.SerializerMethodField()
    telegram_username = serializers.SerializerMethodField()
    contact = serializers.SerializerMethodField()
    track_name = serializers.CharField(source="track.name", read_only=True)
    track = serializers.CharField(source="track.name", read_only=True)
    created_date = serializers.SerializerMethodField()

    class Meta:
        model = Match
        fields = [
            "id",
            "partner_id",
            "partner_user_id",
            "telegram_username",
            "full_name",
            "city",
            "contact",
            "track",
            "track_name",
            "status",
            "created_at",
            "created_date",
        ]

    def _get_other_user(self, obj: Match):
        request = self.context.get("request")
        if request and request.user == obj.user_a:
            return obj.user_b
        return obj.user_a

    def get_partner_id(self, obj: Match) -> int:
        other = self._get_other_user(obj)
        return other.id if other else 0

    def get_partner_user_id(self, obj: Match) -> int:
        return self.get_partner_id(obj)

    def get_telegram_username(self, obj: Match) -> str:
        other = self._get_other_user(obj)
        return other.telegram_username if other else ""

    def get_contact(self, obj: Match) -> dict:
        other = self._get_other_user(obj)
        if not other:
            return {"telegram": "", "email": ""}
        telegram = f"@{other.telegram_username}" if other.telegram_username else ""
        return {
            "telegram": telegram,
            "email": other.email or "",
        }

    def get_full_name(self, obj: Match) -> str:
        other = self._get_other_user(obj)
        profile = getattr(other, "profile", None)
        return profile.full_name if profile else ""

    def get_city(self, obj: Match) -> str:
        other = self._get_other_user(obj)
        profile = getattr(other, "profile", None)
        return profile.city if profile else ""

    def get_created_date(self, obj: Match):
        return obj.created_at.date() if obj.created_at else None
