# Proposed EduMate models. Split by app as marked by the "# apps/..." headers.
# Assumes apps.common.models.BaseModel (abstract: id, created_at, updated_at)
# and Django 5.1+ (CheckConstraint uses `condition=`).

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import F, Q

from apps.common.models import BaseModel

User = settings.AUTH_USER_MODEL


# ---------------------------------------------------------------- apps/users
# Profile: keep your fields, ADD these two, REMOVE `rating` (see notes).
class Profile(BaseModel):
    class AgeGroup(models.TextChoices):
        UNDER_18 = "under_18", "Under 18"
        ADULT = "adult", "18+"

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    full_name = models.CharField(max_length=100)
    city = models.CharField(max_length=100, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    image = models.ImageField(upload_to="profile/", null=True, blank=True)
    age_group = models.CharField(max_length=10, choices=AgeGroup.choices)  # matching safety
    is_hidden = models.BooleanField(default=False)

    # Cached stats, recomputed from Session/Review (never edited by the user)
    sessions_completed = models.PositiveIntegerField(default=0)
    avg_rating = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)


# -------------------------------------------------------------- apps/catalog
class Track(BaseModel):
    """What people study: 'ielts-speaking', 'sat-math', 'python'. A table, not an enum,
    so new directions are added from the admin without a migration."""

    class Category(models.TextChoices):
        EXAM = "exam", "Exam"
        TECH = "tech", "Technology"

    slug = models.SlugField(unique=True)
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=10, choices=Category.choices)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


# --------------------------------------------------------------- apps/goals
class Goal(BaseModel):
    """One user's goal inside one track. Matching works on Goal, not on 'interests'."""

    class Level(models.IntegerChoices):
        BEGINNER = 1
        ELEMENTARY = 2
        INTERMEDIATE = 3
        UPPER = 4
        ADVANCED = 5

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="goals")
    track = models.ForeignKey(Track, on_delete=models.PROTECT, related_name="goals")
    current_level = models.IntegerField(choices=Level.choices)  # normalized, used for matching
    target_level = models.IntegerField(choices=Level.choices)
    current_score = models.DecimalField(max_digits=6, decimal_places=1, null=True, blank=True)  # IELTS 6.0 / SAT 1200, display only
    target_score = models.DecimalField(max_digits=6, decimal_places=1, null=True, blank=True)
    deadline = models.DateField(null=True, blank=True)
    weekly_hours = models.PositiveSmallIntegerField(default=3)
    is_active = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "track"], name="unique_goal_per_track"),
        ]


class Availability(BaseModel):
    """When the user can study with a partner. Without this, matching is useless."""

    class Slot(models.TextChoices):
        MORNING = "morning", "Morning"
        AFTERNOON = "afternoon", "Afternoon"
        EVENING = "evening", "Evening"

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="availability")
    weekday = models.PositiveSmallIntegerField(validators=[MaxValueValidator(6)])  # 0 = Monday
    slot = models.CharField(max_length=10, choices=Slot.choices)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "weekday", "slot"], name="unique_availability"),
        ]


# ------------------------------------------------------------ apps/matching
class MatchRequest(BaseModel):
    """Directed: who asked whom. The Match is created only when this is accepted."""

    class Status(models.TextChoices):
        PENDING = "pending"
        ACCEPTED = "accepted"
        DECLINED = "declined"
        CANCELED = "canceled"

    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="requests_sent")
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="requests_received")
    track = models.ForeignKey(Track, on_delete=models.PROTECT)
    message = models.CharField(max_length=200, blank=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    responded_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.CheckConstraint(condition=~Q(from_user=F("to_user")), name="no_self_request"),
            models.UniqueConstraint(fields=["from_user", "to_user", "track"], name="unique_request"),
        ]


class Match(BaseModel):
    """Symmetric pair. user_a < user_b is enforced so (A,B) and (B,A) can't both exist."""

    class Status(models.TextChoices):
        ACTIVE = "active"
        ENDED = "ended"

    user_a = models.ForeignKey(User, on_delete=models.CASCADE, related_name="matches_as_a")
    user_b = models.ForeignKey(User, on_delete=models.CASCADE, related_name="matches_as_b")
    track = models.ForeignKey(Track, on_delete=models.PROTECT)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.ACTIVE)

    class Meta:
        constraints = [
            models.CheckConstraint(condition=Q(user_a__lt=F("user_b")), name="match_ordered_pair"),
            models.UniqueConstraint(fields=["user_a", "user_b", "track"], name="unique_match"),
        ]

    @classmethod
    def create_for(cls, first, second, track):
        a, b = sorted([first, second], key=lambda u: u.pk)
        return cls.objects.create(user_a=a, user_b=b, track=track)


class Session(BaseModel):
    """THE metric: did two people actually study together. Needs both confirmations."""

    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name="sessions")
    happened_at = models.DateTimeField()
    confirmed_by_a = models.BooleanField(default=False)
    confirmed_by_b = models.BooleanField(default=False)

    @property
    def is_confirmed(self):
        return self.confirmed_by_a and self.confirmed_by_b


class Review(BaseModel):
    """The only legitimate source of a rating: feedback after a confirmed session."""

    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name="reviews")
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviews_given")
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.CharField(max_length=300, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["session", "reviewer"], name="one_review_per_session"),
        ]


# ------------------------------------------------------------- apps/safety
class Block(BaseModel):
    blocker = models.ForeignKey(User, on_delete=models.CASCADE, related_name="blocks_made")
    blocked = models.ForeignKey(User, on_delete=models.CASCADE, related_name="blocks_received")

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["blocker", "blocked"], name="unique_block"),
        ]


class Report(BaseModel):
    class Status(models.TextChoices):
        OPEN = "open"
        REVIEWED = "reviewed"

    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reports_made")
    reported = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reports_received")
    reason = models.CharField(max_length=100)
    details = models.TextField(max_length=1000, blank=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.OPEN)


# --------------------------------------------------- apps/showcase (LATER, not MVP)
class Certificate(BaseModel):
    class Status(models.TextChoices):
        SELF_DECLARED = "self_declared"  # shown as unverified
        VERIFIED = "verified"
        REJECTED = "rejected"

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="certificates")
    title = models.CharField(max_length=150)
    issuer = models.CharField(max_length=150)
    issued_date = models.DateField(null=True, blank=True)
    credential_url = models.URLField(blank=True)
    file = models.FileField(upload_to="certificates/", null=True, blank=True)  # private storage
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.SELF_DECLARED)


class PortfolioItem(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="portfolio")
    title = models.CharField(max_length=150)
    description = models.TextField(max_length=1000, blank=True)
    url = models.URLField(blank=True)  # GitHub / demo link, no uploads at first
    tracks = models.ManyToManyField(Track, blank=True, related_name="portfolio_items")