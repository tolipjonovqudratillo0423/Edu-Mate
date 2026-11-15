from datetime import date

from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError

from apps.goals.models import Goal, Availability
from apps.goals.repositories import GoalRepository, AvailabilityRepository
from apps.users.models import User


class GoalService:
    """
    Business rules + validation.
    Views call service only → service calls repository only.
    Raises DRF exceptions so the global exception handler renders them correctly.
    """

    # ------------------------------------------------------------------ #
    # Helpers                                                              #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _validate_levels(current_level: int | None, target_level: int | None) -> None:
        """target_level must be >= current_level."""
        if current_level is not None and target_level is not None:
            if target_level < current_level:
                raise ValidationError(
                    {"target_level": "target_level must be greater than or equal to current_level."}
                )

    @staticmethod
    def _validate_deadline(deadline) -> None:
        """Deadline must not be in the past."""
        if deadline is not None and deadline < date.today():
            raise ValidationError(
                {"deadline": "Deadline cannot be in the past."}
            )

    @staticmethod
    def _validate_weekly_hours(weekly_hours: int | None) -> None:
        """weekly_hours must be between 1 and 40."""
        if weekly_hours is not None and not (1 <= weekly_hours <= 40):
            raise ValidationError(
                {"weekly_hours": "weekly_hours must be between 1 and 40."}
            )

    @staticmethod
    def _check_duplicate(user: User, track_id: int, exclude_id: int = None) -> None:
        """One goal per (user, track)."""
        if GoalRepository.exists_for_user_track(user, track_id, exclude_id):
            raise ValidationError(
                {"track": "You already have a goal for this track."}
            )

    @staticmethod
    def _get_goal_or_404(goal_id: int) -> Goal:
        goal = GoalRepository.get_by_id(goal_id)
        if goal is None:
            raise NotFound("Goal not found.")
        return goal

    @staticmethod
    def _assert_owner(goal: Goal, user: User) -> None:
        if goal.user != user:
            raise PermissionDenied("You do not have permission to modify this goal.")

    @staticmethod
    def _check_visibility(goal: Goal, requesting_user: User) -> None:
        """
        Returns silently if the goal is visible to requesting_user.
        Rules:
          - Owner always sees their own goal.
          - Other users are blocked when profile.is_hidden == True.
        """
        if goal.user == requesting_user:
            return
        try:
            if goal.user.profile.is_hidden:
                raise NotFound("Goal not found.")   # hide existence — not 403
        except Exception:
            # profile not set up yet → treat as hidden
            raise NotFound("Goal not found.")

    # ------------------------------------------------------------------ #
    # Public interface                                                     #
    # ------------------------------------------------------------------ #

    @staticmethod
    def list_my_goals(user: User):
        return GoalRepository.get_all_for_user(user)

    @staticmethod
    def get_goal(goal_id: int, requesting_user: User) -> Goal:
        goal = GoalService._get_goal_or_404(goal_id)
        GoalService._check_visibility(goal, requesting_user)
        return goal

    @staticmethod
    def create_goal(user: User, validated_data: dict) -> Goal:
        track_id = validated_data["track"].pk
        GoalService._check_duplicate(user, track_id)
        GoalService._validate_levels(
            validated_data.get("current_level"),
            validated_data.get("target_level"),
        )
        GoalService._validate_deadline(validated_data.get("deadline"))
        GoalService._validate_weekly_hours(validated_data.get("weekly_hours"))
        return GoalRepository.create(user, validated_data)

    @staticmethod
    def update_goal(goal_id: int, user: User, validated_data: dict, partial: bool = False) -> Goal:
        goal = GoalService._get_goal_or_404(goal_id)
        GoalService._assert_owner(goal, user)

        # track cannot be changed
        if "track" in validated_data and validated_data["track"] != goal.track:
            raise ValidationError({"track": "Track cannot be changed after creation."})

        # pull merged values for cross-field validation
        current_level = validated_data.get("current_level", goal.current_level)
        target_level = validated_data.get("target_level", goal.target_level)
        deadline = validated_data.get("deadline", goal.deadline)
        weekly_hours = validated_data.get("weekly_hours", goal.weekly_hours)

        GoalService._validate_levels(current_level, target_level)
        GoalService._validate_deadline(deadline)
        GoalService._validate_weekly_hours(weekly_hours)

        return GoalRepository.update(goal, validated_data)

    @staticmethod
    def delete_goal(goal_id: int, user: User) -> None:
        goal = GoalService._get_goal_or_404(goal_id)
        GoalService._assert_owner(goal, user)
        GoalRepository.delete(goal)


class AvailabilityService:
    """
    Business rules for Availability.
    Views call service only → service calls repository only.
    Raises DRF exceptions.
    """

    # ------------------------------------------------------------------ #
    # Helpers                                                              #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _get_or_404(avail_id: int) -> Availability:
        avail = AvailabilityRepository.get_by_id(avail_id)
        if avail is None:
            raise NotFound("Availability slot not found.")
        return avail

    @staticmethod
    def _assert_owner(avail: Availability, user: User) -> None:
        if avail.user != user:
            raise PermissionDenied("You do not have permission to modify this slot.")

    @staticmethod
    def _check_duplicate(user: User, weekday: int, slot: str, exclude_id: int = None) -> None:
        """Duplicate (user, weekday, slot) → 400."""
        if AvailabilityRepository.exists_for_user(user, weekday, slot, exclude_id):
            raise ValidationError(
                {"non_field_errors": "You already have this availability slot."}
            )

    # ------------------------------------------------------------------ #
    # Public interface                                                     #
    # ------------------------------------------------------------------ #

    @staticmethod
    def list_my_slots(user: User):
        return AvailabilityRepository.get_all_for_user(user)

    @staticmethod
    def create_slot(user: User, validated_data: dict) -> Availability:
        weekday = validated_data["weekday"]
        slot = validated_data["slot"]
        AvailabilityService._check_duplicate(user, weekday, slot)
        return AvailabilityRepository.create(user, validated_data)

    @staticmethod
    def update_slot(avail_id: int, user: User, validated_data: dict) -> Availability:
        avail = AvailabilityService._get_or_404(avail_id)
        AvailabilityService._assert_owner(avail, user)

        # merge for duplicate check: if weekday/slot not in patch, keep existing
        weekday = validated_data.get("weekday", avail.weekday)
        slot = validated_data.get("slot", avail.slot)
        AvailabilityService._check_duplicate(user, weekday, slot, exclude_id=avail_id)

        return AvailabilityRepository.update(avail, validated_data)

    @staticmethod
    def delete_slot(avail_id: int, user: User) -> None:
        avail = AvailabilityService._get_or_404(avail_id)
        AvailabilityService._assert_owner(avail, user)
        AvailabilityRepository.delete(avail)
