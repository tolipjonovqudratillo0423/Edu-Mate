"""
Tests for the Goals API.

Coverage matrix:
  GoalListCreateView  GET  → list own goals (success, anonymous 401)
  GoalListCreateView  POST → create (success, duplicate, bad levels,
                              past deadline, bad weekly_hours, anonymous 401)
  GoalDetailView      GET  → own goal, other user visible, hidden owner 404,
                              anonymous 401, non-existent 404
  GoalDetailView      PUT  → owner success, other user 403, track immutable
  GoalDetailView      PATCH→ owner partial success
  GoalDetailView      DELETE → owner success, other user 403, anonymous 401
"""

from datetime import date, timedelta

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.catalog.models import Track
from apps.goals.models import Goal
from apps.users.models import User, Profile


# ------------------------------------------------------------------ #
# Helpers                                                             #
# ------------------------------------------------------------------ #

def make_user(email, password="Pass1234!") -> User:
    return User.objects.create_user(email=email, password=password)


def make_profile(user: User, is_hidden=False) -> Profile:
    return Profile.objects.create(
        user=user,
        full_name=f"User {user.pk}",
        age_group=Profile.AgeGroup.ADULT,
        is_hidden=is_hidden,
    )


def make_track(slug="ielts", name="IELTS", category=Track.Category.EXAM) -> Track:
    return Track.objects.get_or_create(
        slug=slug,
        defaults={"name": name, "category": category},
    )[0]


def make_goal(user: User, track: Track, **kwargs) -> Goal:
    defaults = {
        "current_level": Goal.Level.BEGINNER,
        "target_level": Goal.Level.INTERMEDIATE,
        "weekly_hours": 5,
    }
    defaults.update(kwargs)
    return Goal.objects.create(user=user, track=track, **defaults)


TOMORROW = (date.today() + timedelta(days=1)).isoformat()
YESTERDAY = (date.today() - timedelta(days=1)).isoformat()


# ------------------------------------------------------------------ #
# GoalListCreateView                                                  #
# ------------------------------------------------------------------ #

class GoalListTests(APITestCase):

    def setUp(self):
        self.user = make_user("alice@example.com")
        self.track = make_track()
        self.url = reverse("goal-list-create")

    def test_list_own_goals_success(self):
        make_goal(self.user, self.track)
        self.client.force_authenticate(self.user)
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data["data"]), 1)

    def test_list_returns_only_own_goals(self):
        """Goals of other users must NOT appear."""
        other = make_user("bob@example.com")
        make_goal(other, self.track)
        self.client.force_authenticate(self.user)
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data["data"]), 0)

    def test_list_anonymous_returns_401(self):
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class GoalCreateTests(APITestCase):

    def setUp(self):
        self.user = make_user("alice@example.com")
        self.track = make_track()
        self.url = reverse("goal-list-create")
        self.valid_payload = {
            "track": self.track.pk,
            "current_level": Goal.Level.BEGINNER,
            "target_level": Goal.Level.INTERMEDIATE,
            "weekly_hours": 5,
            "deadline": TOMORROW,
        }

    def test_create_goal_success(self):
        self.client.force_authenticate(self.user)
        res = self.client.post(self.url, self.valid_payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Goal.objects.filter(user=self.user).count(), 1)

    def test_create_duplicate_goal_returns_400(self):
        make_goal(self.user, self.track)
        self.client.force_authenticate(self.user)
        res = self.client.post(self.url, self.valid_payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_target_less_than_current_returns_400(self):
        self.client.force_authenticate(self.user)
        payload = {**self.valid_payload, "current_level": Goal.Level.ADVANCED, "target_level": Goal.Level.BEGINNER}
        res = self.client.post(self.url, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_past_deadline_returns_400(self):
        self.client.force_authenticate(self.user)
        payload = {**self.valid_payload, "deadline": YESTERDAY}
        res = self.client.post(self.url, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_weekly_hours_zero_returns_400(self):
        self.client.force_authenticate(self.user)
        payload = {**self.valid_payload, "weekly_hours": 0}
        res = self.client.post(self.url, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_weekly_hours_above_40_returns_400(self):
        self.client.force_authenticate(self.user)
        payload = {**self.valid_payload, "weekly_hours": 41}
        res = self.client.post(self.url, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_anonymous_returns_401(self):
        res = self.client.post(self.url, self.valid_payload)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


# ------------------------------------------------------------------ #
# GoalDetailView                                                      #
# ------------------------------------------------------------------ #

class GoalDetailGetTests(APITestCase):

    def setUp(self):
        self.owner = make_user("owner@example.com")
        self.other = make_user("other@example.com")
        self.track = make_track()
        self.goal = make_goal(self.owner, self.track)

    def _url(self, pk=None):
        return reverse("goal-detail", kwargs={"pk": pk or self.goal.pk})

    def test_owner_can_read_own_goal(self):
        self.client.force_authenticate(self.owner)
        res = self.client.get(self._url())
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["data"]["id"], self.goal.pk)

    def test_other_user_can_read_goal_if_not_hidden(self):
        make_profile(self.owner, is_hidden=False)
        self.client.force_authenticate(self.other)
        res = self.client.get(self._url())
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_other_user_gets_404_when_owner_is_hidden(self):
        make_profile(self.owner, is_hidden=True)
        self.client.force_authenticate(self.other)
        res = self.client.get(self._url())
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_owner_can_read_own_goal_even_when_hidden(self):
        make_profile(self.owner, is_hidden=True)
        self.client.force_authenticate(self.owner)
        res = self.client.get(self._url())
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_nonexistent_goal_returns_404(self):
        self.client.force_authenticate(self.owner)
        res = self.client.get(self._url(pk=99999))
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_anonymous_returns_401(self):
        res = self.client.get(self._url())
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class GoalUpdateTests(APITestCase):

    def setUp(self):
        self.owner = make_user("owner@example.com")
        self.other = make_user("other@example.com")
        self.track = make_track()
        self.track2 = make_track(slug="sat", name="SAT")
        self.goal = make_goal(self.owner, self.track)
        self.url = reverse("goal-detail", kwargs={"pk": self.goal.pk})

    def test_owner_can_full_update(self):
        self.client.force_authenticate(self.owner)
        payload = {
            "track": self.track.pk,
            "current_level": Goal.Level.BEGINNER,
            "target_level": Goal.Level.ADVANCED,
            "weekly_hours": 10,
        }
        res = self.client.put(self.url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.goal.refresh_from_db()
        self.assertEqual(self.goal.weekly_hours, 10)

    def test_owner_can_partial_update(self):
        self.client.force_authenticate(self.owner)
        res = self.client.patch(self.url, {"weekly_hours": 7})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.goal.refresh_from_db()
        self.assertEqual(self.goal.weekly_hours, 7)

    def test_other_user_update_returns_403(self):
        self.client.force_authenticate(self.other)
        res = self.client.patch(self.url, {"weekly_hours": 7})
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_anonymous_update_returns_401(self):
        res = self.client.patch(self.url, {"weekly_hours": 7})
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_track_cannot_be_changed(self):
        self.client.force_authenticate(self.owner)
        res = self.client.patch(self.url, {"track": self.track2.pk})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_bad_levels_returns_400(self):
        self.client.force_authenticate(self.owner)
        res = self.client.patch(self.url, {
            "current_level": Goal.Level.ADVANCED,
            "target_level": Goal.Level.BEGINNER,
        })
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_past_deadline_returns_400(self):
        self.client.force_authenticate(self.owner)
        res = self.client.patch(self.url, {"deadline": YESTERDAY})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)


class GoalDeleteTests(APITestCase):

    def setUp(self):
        self.owner = make_user("owner@example.com")
        self.other = make_user("other@example.com")
        self.track = make_track()
        self.goal = make_goal(self.owner, self.track)
        self.url = reverse("goal-detail", kwargs={"pk": self.goal.pk})

    def test_owner_can_delete(self):
        self.client.force_authenticate(self.owner)
        res = self.client.delete(self.url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Goal.objects.filter(pk=self.goal.pk).exists())

    def test_other_user_delete_returns_403(self):
        self.client.force_authenticate(self.other)
        res = self.client.delete(self.url)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Goal.objects.filter(pk=self.goal.pk).exists())

    def test_anonymous_delete_returns_401(self):
        res = self.client.delete(self.url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
