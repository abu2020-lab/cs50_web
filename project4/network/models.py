from datetime import datetime
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.CharField(max_length=160, default=None)
    post_date = models.DateTimeField(default=datetime.now, blank=True)

    def __str__(self):
        return f"{self.user} to {self.text}"