from django.contrib import admin

from .models import (
    CustomUser,
    Donation,
    Event,
    Presentation,
    Question,
)


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'telegram_name', 'is_speaker', 'is_organizer')
    search_fields = ('telegram_name',)


@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'summ')


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'start_at')


@admin.register(Presentation)
class PresentationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'topic', 'approved')
    list_filter = ('event',)
    list_editable = ('approved',)


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'presentation')
    list_filter = ('presentation',)
