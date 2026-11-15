"""
Tests for Partners discovery API (apps/matching).

Coverage matrix — Partners:
  - track required (missing parameter -> 400)
  - track invalid format -> 400
  - track nonexistent -> 400
  - excludes self (requesting user's own goal is never in candidates)
  - excludes hidden (profiles with is_hidden=True are excluded)
  - excludes other track (goals in a different track are excluded)
  - excludes pending match requests (both sent by user and received by user)
  - excludes active matches (both as user_a and as user_b)
  - ordering by matching score descending (levels proximity, shared slots, hours proximity)
  - response payload structure verification
  - anonymous request returns 401
"""

from datetime import date, timedelta
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.catalog.models import Track
from apps.goals.models import Goal, Availability
from apps.matching.models import Match, MatchRequest
from apps.users.models import User, Profile


# ------------------------------------------------------------------ #
# Helpers                                                             #
# ------------------------------------------------------------------ #

def make_user(email: str, password: str = "Pass1234!") -> User:
    return User.objects.create_user(email=email, password=password)


def make_profile(user: User, full_name: str = "Test User", is_hidden: bool = False) -> Profile:
    return Profile.objects.create(
        user=user,
        full_name=full_name,
        city="Tashkent",
        age_group=Profile.AgeGroup.ADULT,
        is_hidden=is_hidden,
    )


def make_track(slug: str = "ielts", name: str = "IELTS", category: str = Track.Category.EXAM) -> Track:
    return Track.objects.get_or_create(
        slug=slug,
        defaults={"name": name, "category": category},
    )[0]


def make_goal(user: User, track: Track, **kwargs) -> Goal:
    defaults = {
        "current_level": Goal.Level.INTERMEDIATE,
        "target_level": Goal.Level.ADVANCED,
        "weekly_hours": 5,
        "deadline": date.today() + timedelta(days=60),
    }
    defaults.update(kwargs)
    return Goal.objects.create(user=user, track=track, **defaults)


def make_slot(user: User, weekday: int = 0, slot: str = Availability.Slot.MORNING) -> Availability:
    return Availability.objects.create(user=user, weekday=weekday, slot=slot)


# ------------------------------------------------------------------ #
# Partners API Tests                                                  #
# ------------------------------------------------------------------ #

class PartnersAPITests(APITestCase):

    def setUp(self):
        self.user = make_user("alice@example.com")
        self.profile = make_profile(self.user, full_name="Alice Smith")
        self.track = make_track(slug="ielts", name="IELTS")
        self.user_goal = make_goal(
            self.user,
            self.track,
            current_level=Goal.Level.INTERMEDIATE,  # 3
            weekly_hours=5,
        )
        self.url = reverse("partners")

    def test_track_param_required(self):
        """GET /partners/ without track parameter returns 400."""
        self.client.force_authenticate(self.user)
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_track_invalid_format_returns_400(self):
        """GET /partners/?track=abc returns 400."""
        self.client.force_authenticate(self.user)
        res = self.client.get(f"{self.url}?track=abc")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_track_not_found_returns_400(self):
        """GET /partners/?track=99999 returns 400."""
        self.client.force_authenticate(self.user)
        res = self.client.get(f"{self.url}?track=99999")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_excludes_self(self):
        """User's own goal must not appear in the candidate list."""
        self.client.force_authenticate(self.user)
        res = self.client.get(f"{self.url}?track={self.track.pk}")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        partner_names = [p["full_name"] for p in res.data["data"]]
        self.assertNotIn("Alice Smith", partner_names)
        self.assertEqual(len(res.data["data"]), 0)

    def test_excludes_hidden_profiles(self):
        """Candidates whose profile is_hidden=True must be excluded."""
        hidden_user = make_user("bob_hidden@example.com")
        make_profile(hidden_user, full_name="Bob Hidden", is_hidden=True)
        make_goal(hidden_user, self.track)

        visible_user = make_user("carol_visible@example.com")
        make_profile(visible_user, full_name="Carol Visible", is_hidden=False)
        make_goal(visible_user, self.track)

        self.client.force_authenticate(self.user)
        res = self.client.get(f"{self.url}?track={self.track.pk}")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        names = [p["full_name"] for p in res.data["data"]]
        self.assertIn("Carol Visible", names)
        self.assertNotIn("Bob Hidden", names)

    def test_excludes_other_track_goals(self):
        """Users who have goals in other tracks must not appear for this track."""
        other_track = make_track(slug="sat", name="SAT")
        other_user = make_user("dave@example.com")
        make_profile(other_user, full_name="Dave SAT")
        make_goal(other_user, other_track)

        self.client.force_authenticate(self.user)
        res = self.client.get(f"{self.url}?track={self.track.pk}")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        names = [p["full_name"] for p in res.data["data"]]
        self.assertNotIn("Dave SAT", names)

    def test_excludes_pending_match_request_sent(self):
        """User sent a pending match request to partner -> partner excluded."""
        partner = make_user("eve@example.com")
        make_profile(partner, full_name="Eve Partner")
        make_goal(partner, self.track)

        MatchRequest.objects.create(
            from_user=self.user,
            to_user=partner,
            track=self.track,
            status=MatchRequest.Status.PENDING,
        )

        self.client.force_authenticate(self.user)
        res = self.client.get(f"{self.url}?track={self.track.pk}")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        names = [p["full_name"] for p in res.data["data"]]
        self.assertNotIn("Eve Partner", names)

    def test_excludes_pending_match_request_received(self):
        """Partner sent a pending match request to user -> partner excluded."""
        partner = make_user("frank@example.com")
        make_profile(partner, full_name="Frank Partner")
        make_goal(partner, self.track)

        MatchRequest.objects.create(
            from_user=partner,
            to_user=self.user,
            track=self.track,
            status=MatchRequest.Status.PENDING,
        )

        self.client.force_authenticate(self.user)
        res = self.client.get(f"{self.url}?track={self.track.pk}")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        names = [p["full_name"] for p in res.data["data"]]
        self.assertNotIn("Frank Partner", names)

    def test_excludes_active_match(self):
        """User and partner share an active match -> partner excluded."""
        partner_a = make_user("george@example.com")
        make_profile(partner_a, full_name="George Active")
        make_goal(partner_a, self.track)

        Match.create_for(self.user, partner_a, self.track)

        self.client.force_authenticate(self.user)
        res = self.client.get(f"{self.url}?track={self.track.pk}")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        names = [p["full_name"] for p in res.data["data"]]
        self.assertNotIn("George Active", names)

    def test_ordering_by_matching_score(self):
        """
        Verify partners are sorted by score descending:
        Scoring:
          +3 if |current_level diff| <= 1
          +2 per shared (weekday, slot) up to 3 slots
          +1 if |weekly_hours diff| <= 2

        Self: level=3 (INTERMEDIATE), weekly_hours=5, slots=[(0, MORNING), (1, EVENING)]
        """
        make_slot(self.user, weekday=0, slot=Availability.Slot.MORNING)
        make_slot(self.user, weekday=1, slot=Availability.Slot.EVENING)

        # High match:
        # level=3 (diff 0 <= 1 -> +3)
        # weekly_hours=5 (diff 0 <= 2 -> +1)
        # shared slots: 2 shared (0, MORNING) & (1, EVENING) -> 2 * 2 = +4
        # Total score = 3 + 1 + 4 = 8
        high_user = make_user("high@example.com")
        make_profile(high_user, full_name="High Match")
        make_goal(high_user, self.track, current_level=Goal.Level.INTERMEDIATE, weekly_hours=5)
        make_slot(high_user, weekday=0, slot=Availability.Slot.MORNING)
        make_slot(high_user, weekday=1, slot=Availability.Slot.EVENING)

        # Medium match:
        # level=4 (diff 1 <= 1 -> +3)
        # weekly_hours=6 (diff 1 <= 2 -> +1)
        # shared slots: None -> +0
        # Total score = 3 + 1 = 4
        med_user = make_user("med@example.com")
        make_profile(med_user, full_name="Medium Match")
        make_goal(med_user, self.track, current_level=Goal.Level.UPPER, weekly_hours=6)
        make_slot(med_user, weekday=5, slot=Availability.Slot.AFTERNOON)

        # Low match:
        # level=1 (diff 2 > 1 -> +0)
        # weekly_hours=10 (diff 5 > 2 -> +0)
        # shared slots: None -> +0
        # Total score = 0
        low_user = make_user("low@example.com")
        make_profile(low_user, full_name="Low Match")
        make_goal(low_user, self.track, current_level=Goal.Level.BEGINNER, weekly_hours=10)

        self.client.force_authenticate(self.user)
        res = self.client.get(f"{self.url}?track={self.track.pk}")
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        data = res.data["data"]
        self.assertEqual(len(data), 3)

        # Verify ordering: High Match (8) > Medium Match (4) > Low Match (0)
        self.assertEqual(data[0]["full_name"], "High Match")
        self.assertEqual(data[0]["score"], 8)
        self.assertEqual(data[1]["full_name"], "Medium Match")
        self.assertEqual(data[1]["score"], 4)
        self.assertEqual(data[2]["full_name"], "Low Match")
        self.assertEqual(data[2]["score"], 0)

        # Verify response structure for first partner
        first = data[0]
        self.assertEqual(first["track"], self.track.name)
        self.assertEqual(first["track_name"], self.track.name)
        self.assertIn("city", first)
        self.assertIn("age_group", first)
        self.assertIn("goal", first)
        self.assertEqual(first["goal"]["current_level"], Goal.Level.INTERMEDIATE)
        self.assertEqual(first["goal"]["weekly_hours"], 5)
        self.assertIn("availability", first)
        self.assertEqual(len(first["availability"]), 2)

    def test_anonymous_returns_401(self):
        """Anonymous user cannot access /partners/."""
        res = self.client.get(f"{self.url}?track={self.track.pk}")
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
