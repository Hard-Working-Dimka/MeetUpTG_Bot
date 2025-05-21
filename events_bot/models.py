from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    ROLES = [
        ('organizer', 'Организатор'),
        ('speaker', 'Выступающий'),
        ('listener', 'Слушатель'),
    ]
    telegram_id = models.CharField(max_length=50, unique=True, blank=True, null=True)
    telegram_name = models.CharField(max_length=255, blank=True, null=True)
    role = models.CharField(max_length=30, choices=ROLES)
    # из анкеты знакомств
    about_user = models.TextField(blank=True, null=True)
    stack = models.TextField(blank=True, null=True)
    grade = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.username


class Event(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    info = models.TextField(blank=True, null=True)
    start_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.name


class Presentation(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    topic = models.CharField(max_length=255, blank=True, null=True)
    start_at = models.DateTimeField(blank=True, null=True)
    end_at = models.DateTimeField(blank=True, null=True)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    approved = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return self.topic


class Question(models.Model):
    presentation = models.ForeignKey(Presentation, on_delete=models.CASCADE, related_name="questions")
    question_text = models.CharField(max_length=255, blank=True, null=True)
    answered = models.BooleanField(default=False)

    def __str__(self):
        return self.question_text


class Donation(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    summ = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.summ


class BroadcastMessage(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="broadcasts")
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

