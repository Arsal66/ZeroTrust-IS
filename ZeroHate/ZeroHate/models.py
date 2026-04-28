from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    is_active = models.BooleanField(default=False)


class LoginOTP(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    login_counts = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)


class ClassificationResult(models.Model):
    """
    Model to store classification results
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='classifications')
    input_text = models.TextField()
    toxic = models.FloatField(default=0.0)
    severe_toxic = models.FloatField(default=0.0)
    obscene = models.FloatField(default=0.0)
    threat = models.FloatField(default=0.0)
    insult = models.FloatField(default=0.0)
    identity_hate = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Classification for {self.user.username} at {self.created_at}"
    
    @property
    def is_neutral(self):
        """Check if all classification values are below threshold"""
        threshold = 0.5  # Assuming 0.5 is the threshold for binary classification
        return (self.toxic < threshold and 
                self.severe_toxic < threshold and 
                self.obscene < threshold and 
                self.threat < threshold and 
                self.insult < threshold and 
                self.identity_hate < threshold)