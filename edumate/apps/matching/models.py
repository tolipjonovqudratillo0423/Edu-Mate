from django.db import models
from django.db.models import F, Q
from django.core.validators import MaxValueValidator, MinValueValidator

from apps.common.models import BaseModel
from apps.users.models import User
from apps.catalog.models import Track


class MatchRequest(BaseModel):
    """Directed: who asked whom. The Match is created only when this is accepted."""

    class Status(models.TextChoices):
        PENDING = "pending"
        ACCEPTED = "accepted"
        DECLINED = "declined"
        CANCELED = "canceled"

    from_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="requests_sent"
    )
    
    to_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="requests_received"
    )
    track = models.ForeignKey(
        Track,
        on_delete=models.PROTECT
    )
    message = models.CharField(
        max_length=200,
        blank=True
    )
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.PENDING
    )
    responded_at = models.DateTimeField(
        null=True,
        blank=True
    )

    class Meta:
        
        verbose_name = "Match Request"
        verbose_name_plural = "Match Requests"
        
        constraints = [
            models.CheckConstraint(
                condition=~Q(from_user=F("to_user")),
                name="no_self_request"
            ),
            models.UniqueConstraint(
                fields=["from_user", "to_user", "track"],
                name="unique_request"
            ),
        ]
        
        indexes = [
            models.Index(
                fields=["from_user", "status"],
                name="from_user_status_idx"
                ),
            models.Index(
                fields=["to_user", "status"],
                name="to_user_status_idx"
                ),           
        ]


class Match(BaseModel):
    """Symmetric pair. user_a < user_b is enforced so (A,B) and (B,A) can't both exist."""

    class Status(models.TextChoices):
        ACTIVE = "active"
        ENDED = "ended"

    user_a = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name="matches_as_a"
    )
    user_b = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name="matches_as_b"
    )
    track = models.ForeignKey(
        Track, on_delete=models.PROTECT
    )
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.ACTIVE
    )

    class Meta:
        
        verbose_name = "Match"
        verbose_name_plural = "Matches"
        
        constraints = [
            models.CheckConstraint(
                condition=Q(user_a__lt=F("user_b")),
                name="match_ordered_pair"
            ),
            models.UniqueConstraint(
                fields=["user_a", "user_b", "track"],
                name="unique_match"
            ),
        ]

    
    @classmethod
    def create_for(cls, first, second, track):
        a, b = sorted([first, second], key=lambda u: u.pk)
        return cls.objects.create(user_a=a, user_b=b, track=track)


class Session(BaseModel):
    """THE metric: did two people actually study together. Needs both confirmations."""

    match = models.ForeignKey(
        Match, on_delete=models.CASCADE, 
        related_name="sessions"
    )
    happened_at = models.DateTimeField()
    
    confirmed_by_a = models.BooleanField(
        default=False
    )
    confirmed_by_b = models.BooleanField(
        default=False
    )

    @property
    def is_confirmed(self):
        return self.confirmed_by_a and self.confirmed_by_b
    
    class Meta:
        
        verbose_name = "Session"
        verbose_name_plural = "Sessions"
        
        indexes = [
            models.Index(
                fields=['match', 'happened_at'],
                name='match_happened_at_idx'
            ),
            
        ]
        
        


class Review(BaseModel):
    """The only legitimate source of a rating: feedback after a confirmed session."""

    session = models.ForeignKey(
        Session, on_delete=models.CASCADE,
        related_name="reviews"
    )
    reviewer = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name="reviews_given"
    )
    rating = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5)
        ]
    )
    comment = models.CharField(
        max_length=300,
        blank=True
    )

    class Meta:
        
        verbose_name = "Review"
        verbose_name_plural = "Reviews"
        
        constraints = [
            models.UniqueConstraint(
                fields=["session", "reviewer"],
                name="one_review_per_session"
            ),
        ]

