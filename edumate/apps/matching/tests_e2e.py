from django.core.management import call_command
from rest_framework import status
from rest_framework.test import APITestCase

from apps.catalog.models import Track
from apps.users.models import User


class DemoApiFlowTests(APITestCase):
    def test_demo_path_from_login_to_active_mate(self):
        call_command("seed_demo")

        login = self.client.post(
            "/auth/login/",
            {"email": "demo0@edumate.demo", "password": "demo12345"},
            format="json",
        )
        self.assertEqual(login.status_code, status.HTTP_200_OK)
        tokens = login.data["data"]["tokens"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {tokens['access']}")

        track = Track.objects.get(slug="ielts-speaking")
        goal = self.client.post(
            "/goals/",
            {
                "track": track.id,
                "current_level": 3,
                "target_level": 4,
                "current_score": 6.0,
                "target_score": 7.0,
                "deadline": "2026-12-31",
                "weekly_hours": 6,
            },
            format="json",
        )
        self.assertEqual(goal.status_code, status.HTTP_201_CREATED)

        for weekday, slot in ((0, "evening"), (1, "evening"), (2, "afternoon")):
            response = self.client.post(
                "/availability/", {"weekday": weekday, "slot": slot}, format="json"
            )
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        partners_response = self.client.get(f"/partners/?track={track.id}")
        self.assertEqual(partners_response.status_code, status.HTTP_200_OK)
        payload = partners_response.data["data"]
        self.assertIn("max_score", payload)
        partners = payload["results"]
        self.assertTrue(partners)
        demo0 = User.objects.get(email="demo0@edumate.demo")
        self.assertNotIn(demo0.id, [partner["user_id"] for partner in partners])
        partner_id = partners[0]["user_id"]

        created = self.client.post(
            "/match-requests/",
            {"to_user": partner_id, "track": track.id, "message": "Let's study together"},
            format="json",
        )
        self.assertEqual(created.status_code, status.HTTP_201_CREATED)

        received = self.client.get("/match-requests/?box=received")
        self.assertEqual(received.status_code, status.HTTP_200_OK)
        incoming = received.data["data"]
        seeded = next(
            request for request in incoming
            if request["from_user"] in [
                User.objects.get(email="demo1@edumate.demo").id,
                User.objects.get(email="demo2@edumate.demo").id,
            ]
        )
        self.assertEqual(seeded["status"], "pending")

        accepted = self.client.patch(
            f"/match-requests/{seeded['id']}/", {"status": "accepted"}, format="json"
        )
        self.assertEqual(accepted.status_code, status.HTTP_200_OK)
        repeated = self.client.patch(
            f"/match-requests/{seeded['id']}/", {"status": "accepted"}, format="json"
        )
        self.assertEqual(repeated.status_code, status.HTTP_400_BAD_REQUEST)

        mates = self.client.get("/mates/?status=active")
        self.assertEqual(mates.status_code, status.HTTP_200_OK)
        self.assertIn(
            seeded["from_user"],
            [mate["partner_id"] for mate in mates.data["data"]],
        )
