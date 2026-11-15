from django.db.models import Prefetch, Q

from apps.catalog.models import Track
from apps.goals.models import Goal, Availability
from apps.matching.models import Match, MatchRequest
from apps.users.models import User


class PartnersRepository:
    """
    Pure ORM layer for the partners/discovery feature.
    No business rules, no DRF imports.
    All heavy lifting (prefetch, exclusion sets) lives here so the service
    can work purely with Python objects — zero N+1 queries.
    """

    @staticmethod
    def get_track_or_none(track_id: int) -> Track | None:
        try:
            return Track.objects.get(pk=track_id)
        except (Track.DoesNotExist, ValueError):
            return None

    @staticmethod
    def get_user_goal_for_track(user: User, track_id: int) -> Goal | None:
        try:
            return Goal.objects.get(user=user, track_id=track_id)
        except Goal.DoesNotExist:
            return None

    @staticmethod
    def get_user_availability(user: User) -> list[Availability]:
        return list(Availability.objects.filter(user=user))

    @staticmethod
    def get_candidate_user_ids_with_active_match(user: User, track_id: int) -> set[int]:
        """
        Returns PKs of users who already share an ACTIVE Match with `user`
        for the given track.
        """
        active = Match.objects.filter(
            track_id=track_id,
            status=Match.Status.ACTIVE,
        ).filter(
            Q(user_a=user) | Q(user_b=user)
        ).values_list("user_a_id", "user_b_id")

        excluded = set()
        for a_id, b_id in active:
            excluded.add(a_id)
            excluded.add(b_id)
        excluded.discard(user.pk)
        return excluded

    @staticmethod
    def get_candidate_user_ids_with_pending_request(user: User, track_id: int) -> set[int]:
        """
        Returns PKs of users who have a PENDING MatchRequest with `user`
        (in either direction) for the given track.
        """
        pending = MatchRequest.objects.filter(
            track_id=track_id,
            status=MatchRequest.Status.PENDING,
        ).filter(
            Q(from_user=user) | Q(to_user=user)
        ).values_list("from_user_id", "to_user_id")

        excluded = set()
        for from_id, to_id in pending:
            excluded.add(from_id)
            excluded.add(to_id)
        excluded.discard(user.pk)
        return excluded

    @staticmethod
    def get_candidates(user: User, track_id: int, exclude_user_ids: set[int]):
        """
        Returns Goal queryset for `track_id`, excluding:
          - the requesting user
          - users whose profile is hidden or missing
          - any user id in `exclude_user_ids`

        Each Goal has:
          - goal.user.profile  (via select_related)
          - goal.user.availability_slots  (prefetched list of Availability)
        """
        return (
            Goal.objects
            .filter(track_id=track_id)
            .exclude(user=user)
            .exclude(user_id__in=exclude_user_ids)
            .exclude(user__profile__is_hidden=True)
            .filter(user__profile__isnull=False)
            .select_related("user__profile", "track")
            .prefetch_related(
                Prefetch(
                    "user__availability",
                    queryset=Availability.objects.all(),
                    to_attr="availability_slots",
                )
            )
            .order_by("user_id")
        )
