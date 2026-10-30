from django.db import models

from apps.common.models import BaseModel


class Track(BaseModel):
    
    class Category(models.TextChoices):
        EXAM = "exam", "Exam"
        TECH = "tech", "Technology"
    
    slug = models.SlugField(
        unique=True
    )
    name = models.CharField(
        max_length=100
    )
    
    category = models.CharField(
        max_length=10,
        choices=Category.choices,
    )
    
    def __str__(self):
        return f"{self.name} --- {self.slug}"

    class Meta:
        verbose_name = "Track"
        verbose_name_plural = "Tracks"
        