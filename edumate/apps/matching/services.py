from dataclasses import dataclass, field

from rest_framework.exceptions import ValidationError

from apps.goals.models import Goal
from apps.matching.repositories import PartnersRepository
from apps.users.models import User


# ------------------------------------------------------------------ #
# Scoring constants                                                   #
# ------------------------------------------------------------------ #
SCORE_LEVEL_CLOSE = 3        # |current_level diff| <= 1
SCORE_PER_SHARED_SLOT = 2    # per shared (weekday, slot), max 3 slots
MAX_SHARED_SLOTS = 3
SCORE_HOURS_CLOSE = 1        # |weekly_hours diff| <= 2
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
        """
        Main entry point.
        1. Validate track exists.
        2. Find exclusion sets (active match, pending request).
        3. Fetch candidates (no N+1).
        4. Score + sort.
        5. Return top 20.
        """
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

        # Sort by score descending, top 20
        results.sort(key=lambda r: r.score, reverse=True)
        return results[:TOP_N]
