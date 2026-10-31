from django.db import models
from django.core.validators import MaxValueValidator

from apps.common.models import BaseModel
from apps.catalog.models import Track
from apps.users.models import User


class Goal(BaseModel):
    """One user's goal inside one track. Matching works on Goal, not on 'interests'."""

    class Level(models.IntegerChoices):
        BEGINNER = 1
        ELEMENTARY = 2
        INTERMEDIATE = 3
        UPPER = 4
        ADVANCED = 5

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="goals"
    )
    track = models.ForeignKey(
        Track,
        on_delete=models.PROTECT,
        related_name="goals"
    )
    current_level = models.IntegerField(  # normalized, used for matching
        choices=Level.choices
    )  
    target_level = models.IntegerField(
        choices=Level.choices
    )
    current_score = models.DecimalField(  # IELTS 6.0 / SAT 1200, display only
        max_digits=6,
        decimal_places=1,
        null=True,
        blank=True 
    )  
    target_score = models.DecimalField(
        max_digits=6,
        decimal_places=1,
        null=True,
        blank=True
    )
    deadline = models.DateField(
        null=True,
        blank=True
    )
    weekly_hours = models.PositiveSmallIntegerField(
        default=3
    )
    

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "user",
                    "track"
                ], 
                name="unique_goal_per_track"
            ),
        ]
        
        indexes = [
            models.Index(
                fields=["track", "user"],
                name="track_user_idx"
            ),
            models.Index(
                fields=["track", "target_level"],
                name="track_target_level_idx"
            ),
            models.Index(
                fields=["track", "current_level"],
                name="track_current_level_idx"
            ),
            models.Index(
                fields=["track", "deadline"],
                name="track_deadline_idx"
            ),
        ]


class Availability(BaseModel):
    """When the user can study with a partner. Without this, matching is useless."""

    class Slot(models.TextChoices):
        MORNING = "morning", "Morning"
        AFTERNOON = "afternoon", "Afternoon"
        EVENING = "evening", "Evening"


    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="availability"
    )
    weekday = models.PositiveSmallIntegerField(
        validators=[
            MaxValueValidator(6)# 0 = Monday
        ]
    )  
    slot = models.CharField(
        max_length=10, 
        choices=Slot.choices
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "user",
                    "weekday",
                    "slot"
                ],
                name="unique_availability"
            ),
        ]
    

