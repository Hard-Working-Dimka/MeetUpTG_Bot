from django.contrib import admin
from .models import CustomUser, Event, Presentation, Question, Donation, BroadcastMessage
from django.contrib.auth.admin import UserAdmin


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser

    fieldsets = (
        *UserAdmin.fieldsets,
        (
            'Дополнительная информация',
            {
                'fields': (
                    'telegram_id',
                    'telegram_name',
                    'full_name',
                    'phone_number',
                    'role',
                    'about_user',
                    'stack',
                    'grade',
                ),
            },
        ),
    )
    list_display = ('username', 'email', 'first_name', 'last_name', 'role')


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
