from dataclasses import dataclass, field
from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import NotFound, ValidationError

from apps.goals.models import Goal
from apps.matching.models import Match, MatchRequest
from apps.matching.repositories import (
    PartnersRepository,
    MatchRequestRepository,
    MatchRepository,
)
from apps.users.models import User


# ------------------------------------------------------------------ #
# Partners Discovery Service                                         #
# ------------------------------------------------------------------ #

SCORE_LEVEL_CLOSE = 3        # |current_level diff| <= 1
SCORE_PER_SHARED_SLOT = 2    # per shared (weekday, slot), max 3 slots
MAX_SHARED_SLOTS = 3
SCORE_HOURS_CLOSE = 1        # |weekly_hours diff| <= 2
MAX_SCORE = SCORE_LEVEL_CLOSE + MAX_SHARED_SLOTS * SCORE_PER_SHARED_SLOT + SCORE_HOURS_CLOSE
TOP_N = 20


@dataclass
class PartnerResult:
    """
    Plain Python object passed from service → serializer.
    Keeps the view/serializer free from scoring logic.
    """
    goal: Goal
    score: int
    shared_slots: list = field(default_factory=list)


class PartnersService:
    """
    Business rules for the partner discovery feature.
    Views call service only → service calls repository only.
    Raises DRF exceptions.
    """

    @staticmethod
    def _score(my_goal: Goal | None, my_slots: list, candidate_goal: Goal) -> tuple[int, list]:
        """
        Returns (score, shared_slots_list).
        Scoring rules:
          +3  if |current_level - candidate.current_level| <= 1
          +2  per shared (weekday, slot) — capped at 3 shared slots
          +1  if |weekly_hours - candidate.weekly_hours| <= 2
        """
        score = 0

        # Level proximity and Weekly hours proximity (if requesting user has a goal)
        if my_goal is not None:
            if abs(my_goal.current_level - candidate_goal.current_level) <= 1:
                score += SCORE_LEVEL_CLOSE

            if abs(my_goal.weekly_hours - candidate_goal.weekly_hours) <= 2:
                score += SCORE_HOURS_CLOSE

        # Shared availability slots
        my_slot_set = {(s.weekday, s.slot) for s in my_slots}
        candidate_slots = getattr(candidate_goal.user, "availability_slots", [])
        shared = [s for s in candidate_slots if (s.weekday, s.slot) in my_slot_set]
        capped = shared[:MAX_SHARED_SLOTS]
        score += len(capped) * SCORE_PER_SHARED_SLOT

        return score, capped

    @staticmethod
    def find_partners(user: User, track_id: int) -> list[PartnerResult]:
        track = PartnersRepository.get_track_or_none(track_id)
        if track is None:
            raise ValidationError({"track": "Track not found or invalid."})

        my_goal = PartnersRepository.get_user_goal_for_track(user, track_id)
        my_slots = PartnersRepository.get_user_availability(user)

        active_ids = PartnersRepository.get_candidate_user_ids_with_active_match(user, track_id)
        pending_ids = PartnersRepository.get_candidate_user_ids_with_pending_request(user, track_id)
        exclude_ids = active_ids | pending_ids

        candidates = PartnersRepository.get_candidates(user, track_id, exclude_ids)

        results = []
        for candidate_goal in candidates:
            score, shared = PartnersService._score(my_goal, my_slots, candidate_goal)
            results.append(PartnerResult(goal=candidate_goal, score=score, shared_slots=shared))

        results.sort(key=lambda r: r.score, reverse=True)
        return results[:TOP_N]


# ------------------------------------------------------------------ #
# MatchRequest Service                                               #
# ------------------------------------------------------------------ #

class MatchRequestService:
    """
    Business rules and validation for MatchRequests.
    Views call service only → service calls repository only.
    Raises DRF exceptions (NotFound, ValidationError).
    """

    @staticmethod
    def create_request(from_user: User, validated_data: dict) -> MatchRequest:
        to_user = validated_data["to_user"]
        track = validated_data["track"]

        # Rule 1: Cannot send request to oneself
        if to_user == from_user:
            raise ValidationError({"to_user": "You cannot send a match request to yourself."})

        # Rule 2: to_user's profile must not be hidden
        if MatchRequestRepository.is_user_profile_hidden(to_user):
            raise ValidationError({"to_user": "Target user profile is hidden or unavailable."})

        # Rule 3: Either user having no goal in that track -> 400
        if not MatchRequestRepository.user_has_goal_in_track(from_user, track.pk):
            raise ValidationError({"track": "You do not have an active goal in this track."})
        if not MatchRequestRepository.user_has_goal_in_track(to_user, track.pk):
            raise ValidationError({"track": "Target user does not have an active goal in this track."})

        # Rule 4: A request for (me, to_user, track) already exists -> 400
        if MatchRequestRepository.exists_request(from_user, to_user, track.pk):
            raise ValidationError({"non_field_errors": "A match request for this track already exists."})

        # Rule 5: An active Match already exists between us in that track -> 400
        if MatchRequestRepository.has_active_match(from_user, to_user, track.pk):
            raise ValidationError({"non_field_errors": "An active match already exists between you and this user in this track."})

        return MatchRequestRepository.create(from_user, validated_data)

    @staticmethod
    def list_requests(user: User, box: str = "received"):
        if box == "sent":
            return MatchRequestRepository.get_sent_requests(user)
        # Default box is "received"
        return MatchRequestRepository.get_received_requests(user)

    @staticmethod
    def update_request_status(request_id: int, user: User, new_status: str) -> MatchRequest:
        match_request = MatchRequestRepository.get_by_id(request_id)
        # Only a party (sender or recipient) may touch it; strangers get 404
        if match_request is None or (match_request.from_user != user and match_request.to_user != user):
            raise NotFound("Match request not found.")

        # Transitions can only occur from PENDING status
        if match_request.status != MatchRequest.Status.PENDING:
            raise ValidationError({"status": "Only pending match requests can be updated."})

        # Recipient transition rules
        if user == match_request.to_user:
            # One-time limit: The recipient can only respond (accept/decline) once.
            # Once responded_at is populated, subsequent responses are rejected with 400
            # to prevent state flip-flopping or duplicate match creation.
            if match_request.responded_at is not None:
                raise ValidationError({"status": "This match request has already been responded to."})

            if new_status == MatchRequest.Status.ACCEPTED:
                # Atomically accept request and create active Match
                with transaction.atomic():
                    MatchRepository.create_for(match_request.from_user, match_request.to_user, match_request.track)
                    return MatchRequestRepository.save_request(
                        match_request,
                        status=MatchRequest.Status.ACCEPTED,
                        responded_at=timezone.now(),
                    )
            elif new_status == MatchRequest.Status.DECLINED:
                return MatchRequestRepository.save_request(
                    match_request,
                    status=MatchRequest.Status.DECLINED,
                    responded_at=timezone.now(),
                )
            else:
                raise ValidationError({"status": "Recipient can only accept or decline a pending request."})

        # Sender transition rules
        elif user == match_request.from_user:
            if new_status == MatchRequest.Status.CANCELED:
                return MatchRequestRepository.save_request(
                    match_request,
                    status=MatchRequest.Status.CANCELED,
                )
            else:
                raise ValidationError({"status": "Sender can only cancel a pending request."})

        raise ValidationError({"status": "Invalid status transition."})


# ------------------------------------------------------------------ #
# Mates Service                                                      #
# ------------------------------------------------------------------ #

class MatesService:
    """
    Business rules for active and ended matches (Mates).
    Views call service only → service calls repository only.
    Raises DRF exceptions.
    """

    @staticmethod
    def list_mates(user: User, status: str = Match.Status.ACTIVE):
        if status not in [Match.Status.ACTIVE, Match.Status.ENDED]:
            status = Match.Status.ACTIVE
        return MatchRepository.get_matches_for_user(user, status=status)

    @staticmethod
    def end_mate(match_id: int, user: User) -> Match:
        match = MatchRepository.get_by_id(match_id)
        # Either party may touch it; strangers get 404
        if match is None or (match.user_a != user and match.user_b != user):
            raise NotFound("Match not found.")

        # Soft-end: set status to ended, keep row for sessions/reviews history
        return MatchRepository.end_match(match)
