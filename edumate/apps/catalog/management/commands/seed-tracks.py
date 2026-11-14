from django.core.management.base import BaseCommand
 
from apps.catalog.models import Track
 
TRACKS = [
    ("ielts-speaking", "IELTS Speaking", "exam"),
    ("ielts-writing", "IELTS Writing", "exam"),
    ("sat-math", "SAT Math", "exam"),
    ("python", "Python", "tech"),
]
 
 
class Command(BaseCommand):
    help = "Create the starter tracks (safe to run many times)"
 
    def handle(self, *args, **options):
        for slug, name, category in TRACKS:
            _, created = Track.objects.get_or_create(
                slug=slug, defaults={"name": name, "category": category}
            )
            self.stdout.write(f"{'created' if created else 'exists '} {slug}")