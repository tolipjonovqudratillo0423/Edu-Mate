from datetime import date

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.catalog.models import Track
from apps.goals.models import Goal, Availability
from apps.matching.models import MatchRequest
from apps.users.models import User, Profile


class Command(BaseCommand):
    help = "Create the local EduMate demo accounts and matching data."

    @transaction.atomic
    def handle(self, *args, **options):
        ielts, _ = Track.objects.get_or_create(slug="ielts-speaking", defaults={"name": "IELTS Speaking", "category": Track.Category.EXAM})
        sat, _ = Track.objects.get_or_create(slug="sat-math", defaults={"name": "SAT Math", "category": Track.Category.EXAM})
        tracks = [ielts, sat]
        names = ["Madina Azimova", "Jasur Rakhimov", "Aziza Usmanova", "Ali Mirzaev", "Nilufar Karimova", "Bekzod Karimov", "Malika Tursunova", "Sardor Umarov"]
        users = []
        for index, full_name in enumerate(names):
            first, last = full_name.split(" ", 1)
            user, _ = User.objects.get_or_create(email=f"demo{index}@edumate.demo", defaults={"first_name": first, "last_name": last})
            user.first_name, user.last_name = first, last
            user.set_password("demo12345")
            # Seeded demo accounts are ready to use immediately in the frontend.
            user.is_verified = True
            user.is_onboarded = True
            user.save()
            profile, _ = Profile.objects.get_or_create(user=user)
            profile.full_name = full_name
            profile.city = "Fergana" if index % 2 else "Tashkent"
            profile.bio = "(demo) EduMate study partner"
            profile.age_group = "adult" if index > 3 else "under_18"
            profile.save()
            users.append(user)

            Goal.objects.filter(user=user).delete()
            if index:
                for offset in range(1 + (index % 2)):
                    current = 1 + ((index + offset) % 5)
                    track = tracks[(index + offset) % 2]
                    Goal.objects.create(user=user, track=track, current_level=current, target_level=min(5, current + 1), current_score=current, target_score=min(5, current + 1), deadline=date(2026, 12, 31), weekly_hours=4 + index % 6)
            Availability.objects.filter(user=user).delete()
            for slot_index in range(3 + index % 4):
                Availability.objects.create(user=user, weekday=(index + slot_index) % 7, slot=["morning", "afternoon", "evening"][slot_index % 3])

        for sender in users[1:3]:
            MatchRequest.objects.get_or_create(from_user=sender, to_user=users[0], track=ielts, defaults={"message": "Let's study together", "status": MatchRequest.Status.PENDING})
        self.stdout.write(self.style.SUCCESS("Demo data is ready."))
