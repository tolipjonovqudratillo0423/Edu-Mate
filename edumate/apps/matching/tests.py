"""
Tests for apps/matching:
  - Partners discovery API
  - MatchRequest API (Create, List, Patch)
  - Mates API (List, Soft-Delete)

Coverage matrix:
  - Partners:
    * track required, invalid format 400, not found 400
    * excludes self, hidden profiles, other tracks, pending requests, active matches
    * ordering by matching score descending
    * anonymous 401
  - MatchRequest:
    * create: success (201)
    * create: to_user == me (400)
    * create: to_user profile is hidden (400)
    * create: sender has no goal in track (400)
    * create: recipient has no goal in track (400)
    * create: request already exists (400)
    * create: active match already exists (400)
    * create: anonymous 401
    * list: default received
    * list: box=sent
    * list: isolation (only my requests)
    * list: anonymous 401
    * patch: recipient accept creates exactly one Match with ordered pair
    * patch: second response returns 400 (one-time limit)
    * patch: recipient decline success (no Match created)
    * patch: sender cancel success
    * patch: recipient cannot cancel (400)
    * patch: sender cannot accept (400)
    * patch: sender cannot decline (400)
    * patch: stranger gets 404
    * patch: non-pending request returns 400
    * patch: anonymous 401
  - Mates:
    * list: default active
    * list: status=ended filter
    * list: payload structure (other user's full_name, city, track, status, created_date)
    * list: isolation (strangers matches not shown)
    * list: anonymous 401
    * delete: party delete soft-ends instead of deleting row
    * delete: other party (user_b) can also end match
    * delete: stranger gets 404
    * delete: anonymous 401
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


def make_profile(user: User, full_name: str = "Test User", city: str = "Tashkent", is_hidden: bool = False) -> Profile:
    return Profile.objects.create(
        user=user,
        full_name=full_name,
        city=city,
        age_group=Profile.AgeGroup.UNDER_18,
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


# ================================================================== #
# 1. Partners API Tests                                              #
# ================================================================== #

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
        partner_names = [p["full_name"] for p in res.data["data"]["results"]]
        self.assertNotIn("Alice Smith", partner_names)
        self.assertEqual(len(res.data["data"]["results"]), 0)

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
        names = [p["full_name"] for p in res.data["data"]["results"]]
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
        names = [p["full_name"] for p in res.data["data"]["results"]]
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
        names = [p["full_name"] for p in res.data["data"]["results"]]
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
        names = [p["full_name"] for p in res.data["data"]["results"]]
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
        names = [p["full_name"] for p in res.data["data"]["results"]]
        self.assertNotIn("George Active", names)

    def test_ordering_by_matching_score(self):
        make_slot(self.user, weekday=0, slot=Availability.Slot.MORNING)
        make_slot(self.user, weekday=1, slot=Availability.Slot.EVENING)

        # High match: level diff 0 (+3), hours diff 0 (+1), 2 shared slots (+4) = 8
        high_user = make_user("high@example.com")
        make_profile(high_user, full_name="High Match")
        make_goal(high_user, self.track, current_level=Goal.Level.INTERMEDIATE, weekly_hours=5)
        make_slot(high_user, weekday=0, slot=Availability.Slot.MORNING)
        make_slot(high_user, weekday=1, slot=Availability.Slot.EVENING)

        # Medium match: level diff 1 (+3), hours diff 1 (+1), 0 shared slots (+0) = 4
        med_user = make_user("med@example.com")
        make_profile(med_user, full_name="Medium Match")
        make_goal(med_user, self.track, current_level=Goal.Level.UPPER, weekly_hours=6)
        make_slot(med_user, weekday=5, slot=Availability.Slot.AFTERNOON)

        # Low match: level diff 2 (+0), hours diff 5 (+0), 0 shared slots (+0) = 0
        low_user = make_user("low@example.com")
        make_profile(low_user, full_name="Low Match")
        make_goal(low_user, self.track, current_level=Goal.Level.BEGINNER, weekly_hours=10)

        self.client.force_authenticate(self.user)
        res = self.client.get(f"{self.url}?track={self.track.pk}")
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        data = res.data["data"]["results"]
        self.assertIn("max_score", res.data["data"])
        self.assertEqual(len(data), 3)

        self.assertEqual(data[0]["full_name"], "High Match")
        self.assertEqual(data[0]["score"], 8)
        self.assertEqual(data[1]["full_name"], "Medium Match")
        self.assertEqual(data[1]["score"], 4)
        self.assertEqual(data[2]["full_name"], "Low Match")
        self.assertEqual(data[2]["score"], 0)

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
        res = self.client.get(f"{self.url}?track={self.track.pk}")
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


# ================================================================== #
# 2. MatchRequest API Tests (Create, List, Patch)                    #
# ================================================================== #

class MatchRequestCreateTests(APITestCase):

    def setUp(self):
        self.sender = make_user("sender@example.com")
        self.sender_profile = make_profile(self.sender, full_name="Sender User")
        self.recipient = make_user("recipient@example.com")
        self.recipient_profile = make_profile(self.recipient, full_name="Recipient User")
        self.track = make_track(slug="sat", name="SAT")
        make_goal(self.sender, self.track)
        make_goal(self.recipient, self.track)
        self.url = reverse("match-request-list-create")

    def test_create_match_request_success(self):
        self.client.force_authenticate(self.sender)
        payload = {
            "to_user": self.recipient.pk,
            "track": self.track.pk,
            "message": "Let's study together!",
        }
        res = self.client.post(self.url, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(MatchRequest.objects.count(), 1)
        mr = MatchRequest.objects.first()
        self.assertEqual(mr.from_user, self.sender)
        self.assertEqual(mr.to_user, self.recipient)
        self.assertEqual(mr.track, self.track)
        self.assertEqual(mr.status, MatchRequest.Status.PENDING)
        self.assertEqual(mr.message, "Let's study together!")

    def test_create_match_request_to_self_returns_400(self):
        self.client.force_authenticate(self.sender)
        payload = {
            "to_user": self.sender.pk,
            "track": self.track.pk,
            "message": "Self request",
        }
        res = self.client.post(self.url, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(MatchRequest.objects.count(), 0)

    def test_create_match_request_to_hidden_profile_returns_400(self):
        self.recipient_profile.is_hidden = True
        self.recipient_profile.save()

        self.client.force_authenticate(self.sender)
        payload = {
            "to_user": self.recipient.pk,
            "track": self.track.pk,
        }
        res = self.client.post(self.url, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_match_request_sender_has_no_goal_returns_400(self):
        Goal.objects.filter(user=self.sender, track=self.track).delete()

        self.client.force_authenticate(self.sender)
        payload = {
            "to_user": self.recipient.pk,
            "track": self.track.pk,
        }
        res = self.client.post(self.url, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_match_request_recipient_has_no_goal_returns_400(self):
        Goal.objects.filter(user=self.recipient, track=self.track).delete()

        self.client.force_authenticate(self.sender)
        payload = {
            "to_user": self.recipient.pk,
            "track": self.track.pk,
        }
        res = self.client.post(self.url, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_match_request_already_exists_returns_400(self):
        MatchRequest.objects.create(
            from_user=self.sender,
            to_user=self.recipient,
            track=self.track,
            status=MatchRequest.Status.PENDING,
        )

        self.client.force_authenticate(self.sender)
        payload = {
            "to_user": self.recipient.pk,
            "track": self.track.pk,
        }
        res = self.client.post(self.url, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_match_request_active_match_exists_returns_400(self):
        Match.create_for(self.sender, self.recipient, self.track)

        self.client.force_authenticate(self.sender)
        payload = {
            "to_user": self.recipient.pk,
            "track": self.track.pk,
        }
        res = self.client.post(self.url, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_match_request_anonymous_returns_401(self):
        payload = {
            "to_user": self.recipient.pk,
            "track": self.track.pk,
        }
        res = self.client.post(self.url, payload)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class MatchRequestListTests(APITestCase):

    def setUp(self):
        self.user = make_user("user@example.com")
        self.user_profile = make_profile(self.user, full_name="User Profile")
        self.other_1 = make_user("other1@example.com")
        self.other_1_profile = make_profile(self.other_1, full_name="Other One")
        self.other_2 = make_user("other2@example.com")
        self.other_2_profile = make_profile(self.other_2, full_name="Other Two")
        self.track = make_track(slug="ielts", name="IELTS")

        # Request sent by self.user to other_1
        self.sent_req = MatchRequest.objects.create(
            from_user=self.user,
            to_user=self.other_1,
            track=self.track,
            message="Sent by me",
        )
        # Request received by self.user from other_2
        self.received_req = MatchRequest.objects.create(
            from_user=self.other_2,
            to_user=self.user,
            track=self.track,
            message="Received by me",
        )
        # Request between two strangers
        self.stranger_req = MatchRequest.objects.create(
            from_user=self.other_1,
            to_user=self.other_2,
            track=self.track,
            message="Strangers",
        )
        self.url = reverse("match-request-list-create")

    def test_list_received_requests_default(self):
        self.client.force_authenticate(self.user)
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        ids = [item["id"] for item in res.data["data"]]
        self.assertIn(self.received_req.pk, ids)
        self.assertNotIn(self.sent_req.pk, ids)
        self.assertNotIn(self.stranger_req.pk, ids)

    def test_list_sent_requests(self):
        self.client.force_authenticate(self.user)
        res = self.client.get(f"{self.url}?box=sent")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        ids = [item["id"] for item in res.data["data"]]
        self.assertIn(self.sent_req.pk, ids)
        self.assertNotIn(self.received_req.pk, ids)
        self.assertNotIn(self.stranger_req.pk, ids)

    def test_list_anonymous_returns_401(self):
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class MatchRequestPatchTests(APITestCase):

    def setUp(self):
        self.sender = make_user("sender@example.com")
        self.sender_profile = make_profile(self.sender, full_name="Sender")
        self.recipient = make_user("recipient@example.com")
        self.recipient_profile = make_profile(self.recipient, full_name="Recipient")
        self.stranger = make_user("stranger@example.com")
        self.stranger_profile = make_profile(self.stranger, full_name="Stranger")
        self.track = make_track(slug="sat", name="SAT")
        make_goal(self.sender, self.track)
        make_goal(self.recipient, self.track)

        self.match_request = MatchRequest.objects.create(
            from_user=self.sender,
            to_user=self.recipient,
            track=self.track,
            status=MatchRequest.Status.PENDING,
        )
        self.url = reverse("match-request-detail", kwargs={"pk": self.match_request.pk})

    def test_accept_creates_exactly_one_match_with_ordered_pair(self):
        """Recipient accepts -> status accepted, responded_at set, exactly 1 Match with user_a < user_b."""
        self.client.force_authenticate(self.recipient)
        res = self.client.patch(self.url, {"status": MatchRequest.Status.ACCEPTED})
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.match_request.refresh_from_db()
        self.assertEqual(self.match_request.status, MatchRequest.Status.ACCEPTED)
        self.assertIsNotNone(self.match_request.responded_at)

        # Verify exactly one match created
        self.assertEqual(Match.objects.count(), 1)
        match = Match.objects.first()
        self.assertEqual(match.track, self.track)
        self.assertEqual(match.status, Match.Status.ACTIVE)
        # Verify ordered pair invariant: user_a.pk < user_b.pk
        self.assertLess(match.user_a.pk, match.user_b.pk)
        self.assertSetEqual({match.user_a, match.user_b}, {self.sender, self.recipient})

    def test_second_response_returns_400(self):
        """Once responded_at is set, subsequent responses are rejected with 400 (one-time limit)."""
        self.client.force_authenticate(self.recipient)
        res1 = self.client.patch(self.url, {"status": MatchRequest.Status.ACCEPTED})
        self.assertEqual(res1.status_code, status.HTTP_200_OK)

        # Attempt second response (decline)
        res2 = self.client.patch(self.url, {"status": MatchRequest.Status.DECLINED})
        self.assertEqual(res2.status_code, status.HTTP_400_BAD_REQUEST)

        # Attempt second response (accept again)
        res3 = self.client.patch(self.url, {"status": MatchRequest.Status.ACCEPTED})
        self.assertEqual(res3.status_code, status.HTTP_400_BAD_REQUEST)

    def test_recipient_decline_success(self):
        """Recipient declines -> status declined, responded_at set, no Match created."""
        self.client.force_authenticate(self.recipient)
        res = self.client.patch(self.url, {"status": MatchRequest.Status.DECLINED})
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.match_request.refresh_from_db()
        self.assertEqual(self.match_request.status, MatchRequest.Status.DECLINED)
        self.assertIsNotNone(self.match_request.responded_at)
        self.assertEqual(Match.objects.count(), 0)

    def test_sender_cancel_success(self):
        """Sender can cancel pending request."""
        self.client.force_authenticate(self.sender)
        res = self.client.patch(self.url, {"status": MatchRequest.Status.CANCELED})
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.match_request.refresh_from_db()
        self.assertEqual(self.match_request.status, MatchRequest.Status.CANCELED)
        self.assertEqual(Match.objects.count(), 0)

    def test_recipient_cannot_cancel_returns_400(self):
        """Recipient is not allowed to cancel; returns 400."""
        self.client.force_authenticate(self.recipient)
        res = self.client.patch(self.url, {"status": MatchRequest.Status.CANCELED})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_sender_cannot_accept_returns_400(self):
        """Sender cannot accept their own request; returns 400."""
        self.client.force_authenticate(self.sender)
        res = self.client.patch(self.url, {"status": MatchRequest.Status.ACCEPTED})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_sender_cannot_decline_returns_400(self):
        """Sender cannot decline their own request; returns 400."""
        self.client.force_authenticate(self.sender)
        res = self.client.patch(self.url, {"status": MatchRequest.Status.DECLINED})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_stranger_gets_404_on_patch(self):
        """A user who is not a party gets 404 (hidden existence)."""
        self.client.force_authenticate(self.stranger)
        res = self.client.patch(self.url, {"status": MatchRequest.Status.ACCEPTED})
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_patch_anonymous_returns_401(self):
        res = self.client.patch(self.url, {"status": MatchRequest.Status.ACCEPTED})
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


# ================================================================== #
# 3. Mates API Tests (List, Delete)                                  #
# ================================================================== #

class MatesListTests(APITestCase):

    def setUp(self):
        self.user = make_user("me@example.com")
        self.user_profile = make_profile(self.user, full_name="Me", city="Tashkent")
        self.partner_1 = make_user("partner1@example.com")
        self.partner_1_profile = make_profile(self.partner_1, full_name="Bob Partner", city="Samarkand")
        self.partner_2 = make_user("partner2@example.com")
        self.partner_2_profile = make_profile(self.partner_2, full_name="Carol Partner", city="Bukhara")
        self.stranger_1 = make_user("stranger1@example.com")
        self.stranger_2 = make_user("stranger2@example.com")
        make_profile(self.stranger_1, full_name="Stranger One")
        make_profile(self.stranger_2, full_name="Stranger Two")

        self.track = make_track(slug="ielts", name="IELTS")

        # Active match with partner_1
        self.active_match = Match.create_for(self.user, self.partner_1, self.track)

        # Ended match with partner_2
        self.ended_match = Match.create_for(self.user, self.partner_2, self.track)
        self.ended_match.status = Match.Status.ENDED
        self.ended_match.save()

        # Match between strangers
        self.stranger_match = Match.create_for(self.stranger_1, self.stranger_2, self.track)

        self.url = reverse("mate-list")

    def test_list_active_mates_default(self):
        self.client.force_authenticate(self.user)
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        ids = [item["id"] for item in res.data["data"]]
        self.assertIn(self.active_match.pk, ids)
        self.assertNotIn(self.ended_match.pk, ids)
        self.assertNotIn(self.stranger_match.pk, ids)

    def test_list_mates_filters_by_status(self):
        self.client.force_authenticate(self.user)
        res = self.client.get(f"{self.url}?status=ended")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        ids = [item["id"] for item in res.data["data"]]
        self.assertIn(self.ended_match.pk, ids)
        self.assertNotIn(self.active_match.pk, ids)
        self.assertNotIn(self.stranger_match.pk, ids)

    def test_list_mates_payload_fields(self):
        self.client.force_authenticate(self.user)
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        item = res.data["data"][0]
        self.assertEqual(item["full_name"], "Bob Partner")
        self.assertEqual(item["city"], "Samarkand")
        self.assertEqual(item["track"], self.track.name)
        self.assertEqual(item["track_name"], self.track.name)
        self.assertEqual(item["status"], Match.Status.ACTIVE)
        self.assertIn("created_date", item)
        self.assertIn("created_at", item)

    def test_list_mates_anonymous_returns_401(self):
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class MateDeleteTests(APITestCase):

    def setUp(self):
        self.user_a = make_user("user_a@example.com")
        self.user_a_profile = make_profile(self.user_a, full_name="User A")
        self.user_b = make_user("user_b@example.com")
        self.user_b_profile = make_profile(self.user_b, full_name="User B")
        self.stranger = make_user("stranger@example.com")
        self.stranger_profile = make_profile(self.stranger, full_name="Stranger")

        self.track = make_track(slug="sat", name="SAT")
        self.match = Match.create_for(self.user_a, self.user_b, self.track)
        self.url = reverse("mate-detail", kwargs={"pk": self.match.pk})

    def test_party_delete_soft_ends_match(self):
        """DELETE by user_a soft-ends match: status = ended, row still exists in DB."""
        self.client.force_authenticate(self.user_a)
        res = self.client.delete(self.url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        # Verify row still exists in DB (not hard-deleted)
        self.assertTrue(Match.objects.filter(pk=self.match.pk).exists())
        self.match.refresh_from_db()
        self.assertEqual(self.match.status, Match.Status.ENDED)

    def test_other_party_can_also_end_match(self):
        """DELETE by user_b also soft-ends match."""
        self.client.force_authenticate(self.user_b)
        res = self.client.delete(self.url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.match.refresh_from_db()
        self.assertEqual(self.match.status, Match.Status.ENDED)

    def test_stranger_gets_404_on_delete(self):
        """A stranger who is not a party in the match gets 404."""
        self.client.force_authenticate(self.stranger)
        res = self.client.delete(self.url)
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

        # Verify match status remains ACTIVE
        self.match.refresh_from_db()
        self.assertEqual(self.match.status, Match.Status.ACTIVE)

    def test_delete_anonymous_returns_401(self):
        res = self.client.delete(self.url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
