from apps.goals.models import Goal, Availability
from apps.users.models import User


class GoalRepository:
    """Pure ORM layer — no business rules, no DRF imports."""

    @staticmethod
    def get_all_for_user(user: User):
        return (
            Goal.objects
            .filter(user=user)
            .select_related("track")
            .order_by("-created_at")
        )

    @staticmethod
    def get_by_id(goal_id: int) -> Goal | None:
        try:
            return (
                Goal.objects
                .select_related("track", "user__profile")
                .get(pk=goal_id)
            )
        except Goal.DoesNotExist:
            return None

    @staticmethod
    def exists_for_user_track(user: User, track_id: int, exclude_id: int = None) -> bool:
        qs = Goal.objects.filter(user=user, track_id=track_id)
        if exclude_id is not None:
            qs = qs.exclude(pk=exclude_id)
        return qs.exists()

    @staticmethod
    def create(user: User, validated_data: dict) -> Goal:
        return Goal.objects.create(user=user, **validated_data)

    @staticmethod
    def update(goal: Goal, validated_data: dict) -> Goal:
        for attr, value in validated_data.items():
            setattr(goal, attr, value)
        goal.save()
        return goal

    @staticmethod
    def delete(goal: Goal) -> None:
        goal.delete()


class AvailabilityRepository:
    """Pure ORM layer for Availability — no business rules, no DRF imports."""

    @staticmethod
    def get_all_for_user(user: User):
        return (
            Availability.objects
            .filter(user=user)
            .order_by("weekday", "slot")
        )

    @staticmethod
    def get_by_id(avail_id: int) -> Availability | None:
        try:
            return Availability.objects.select_related("user").get(pk=avail_id)
        except Availability.DoesNotExist:
            return None

    @staticmethod
    def exists_for_user(user: User, weekday: int, slot: str, exclude_id: int = None) -> bool:
        qs = Availability.objects.filter(user=user, weekday=weekday, slot=slot)
        if exclude_id is not None:
            qs = qs.exclude(pk=exclude_id)
        return qs.exists()

    @staticmethod
    def create(user: User, validated_data: dict) -> Availability:
        return Availability.objects.create(user=user, **validated_data)

    @staticmethod
    def update(avail: Availability, validated_data: dict) -> Availability:
        for attr, value in validated_data.items():
            setattr(avail, attr, value)
        avail.save()
        return avail

    @staticmethod
    def delete(avail: Availability) -> None:
        avail.delete()
