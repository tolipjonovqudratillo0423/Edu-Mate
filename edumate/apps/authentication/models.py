from datetime import timedelta
from datetime import timezone

from django.db import models

from apps.common.models import BaseModel
from apps.users.models import User


class VerificationCodes(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user} - {self.code}"
    
    def is_expired(self):
        return self.timestamp < timezone.now() - timedelta(minutes=5)
    

class Activity(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    detail = models.TextField()
    
    def __str__(self):
        return f"{self.user} - {self.detail}"
    
    class Meta:
        verbose_name = "Activity"
        verbose_name_plural = "Activities"