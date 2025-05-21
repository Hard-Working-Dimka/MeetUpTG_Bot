from django.contrib import admin
from .models import CustomUser, Event, Presentation, Question, Donation, BroadcastMessage
from django.contrib.auth.admin import UserAdmin


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'email', 'telegram_id', 'is_speaker', 'is_organizer')
    list_filter = ('is_speaker', 'is_organizer', 'is_staff', 'is_superuser')
    search_fields = ('username', 'email', 'telegram_name')
    fieldsets = UserAdmin.fieldsets + (
        ('Telegram Info', {
            'fields': ('telegram_id', 'telegram_name')
        }),
        ('Доп. информация', {
            'fields': ('is_speaker', 'is_organizer', 'about_user', 'stack', 'grade')
        }),
    )


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_at')
    search_fields = ('name',)
    ordering = ('start_at',)


@admin.register(Presentation)
class PresentationAdmin(admin.ModelAdmin):
    list_display = ('topic', 'user', 'event', 'start_at', 'end_at', 'approved')
    list_filter = ('approved', 'event')
    search_fields = ('topic', 'user__username')
    autocomplete_fields = ('user', 'event')


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question_text', 'presentation')
    search_fields = ('question_text', 'presentation__topic')
    autocomplete_fields = ('presentation',)


@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = ('user', 'summ')
    search_fields = ('user__username',)
    autocomplete_fields = ('user',)


@admin.register(BroadcastMessage)
class BroadcastMessageAdmin(admin.ModelAdmin):
    list_display = ('event', 'created_at')
    search_fields = ('text', 'event__name')
    autocomplete_fields = ('event',)
    readonly_fields = ('created_at',)
