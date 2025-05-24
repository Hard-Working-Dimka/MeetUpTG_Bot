from django.db import models
from django.contrib.auth.models import AbstractUser
from phonenumber_field.modelfields import PhoneNumberField


class CustomUser(AbstractUser):
    ROLES = [
        ('organizer', 'Организатор'),
        ('speaker', 'Выступающий'),
        ('listener', 'Слушатель'),
    ]
    telegram_id = models.CharField(
        max_length=50, unique=True, blank=True, null=True)
    telegram_name = models.CharField(max_length=255, blank=True, null=True)
    role = models.CharField(max_length=30, choices=ROLES)
    notifications = models.BooleanField(
        default=False,
        verbose_name="Получать уведомления"
    )
    # из анкеты знакомств
    full_name = models.CharField(max_length=255, blank=True, null=True)
    phone_number = PhoneNumberField(blank=True, null=True, region='RU')
    about_user = models.TextField(blank=True, null=True)
    stack = models.TextField(blank=True, null=True)
    grade = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.username


class Event(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    info = models.TextField(blank=True, null=True)
    start_at = models.DateTimeField(blank=True, null=True)
    end_at = models.DateTimeField(blank=True, null=True)

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
    presentation = models.ForeignKey(
        Presentation, on_delete=models.CASCADE, related_name="questions")
    question_text = models.CharField(max_length=255, blank=True, null=True)
    answered = models.BooleanField(default=False)

    def __str__(self):
        return self.question_text


class Donation(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    summ = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.summ} руб."


class BroadcastMessage(models.Model):
    event = models.ForeignKey(
        Event, on_delete=models.CASCADE, related_name="broadcasts")
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    end_at = models.DateTimeField(blank=True, null=True)


class SpeakerApplication(models.Model):
    STATUS_CHOICES = [
        ('pending', 'На рассмотрении'),
        ('approved', 'Одобрена'),
        ('rejected', 'Отклонена'),
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    topic = models.CharField(max_length=255, verbose_name="Тема выступления")
    description = models.TextField(verbose_name="Описание выступления")
    experience = models.TextField(verbose_name="Опыт в теме")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Заявка от {self.user} на тему '{self.topic}'"