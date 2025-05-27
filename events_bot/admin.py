from django.contrib import admin
from .models import (
    CustomUser,
    Event,
    Presentation,
    Question,
    Donation,
    BroadcastMessage,
    SpeakerApplication
)
from django.contrib.auth.admin import UserAdmin


class PresentationInline(admin.TabularInline):
    model = Presentation
    extra = 0
    fields = ('speaker', 'topic', 'start_at', 'end_at', 'approved')
    autocomplete_fields = ['speaker']


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 0
    fields = ('asker', 'question_text', 'answered')
    readonly_fields = ('created_at',)
    autocomplete_fields = ['asker', 'presentation']


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
                    'notifications',
                ),
            },
        ),
    )
    list_display = ('username', 'email', 'first_name', 'last_name', 'role')


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_at', 'end_at', 'presentations_count')
    search_fields = ('name',)
    ordering = ('-start_at',)
    inlines = [PresentationInline]

    def presentations_count(self, obj):
        return obj.presentations.count()
    presentations_count.short_description = 'Докладов'


@admin.register(Presentation)
class PresentationAdmin(admin.ModelAdmin):
    list_display = ('topic', 'speaker', 'event', 'start_at', 'approved')
    list_filter = ('approved', 'event')
    search_fields = ('topic', 'speaker__username')
    autocomplete_fields = ('speaker', 'event')
    inlines = [QuestionInline]
    ordering = ('-event__start_at', '-start_at')


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('short_question', 'presentation', 'asker', 'speaker', 'answered', 'created_at')
    list_filter = ('answered', 'event', 'presentation')
    search_fields = ('question_text', 'presentation__topic', 'asker__username')
    autocomplete_fields = ('asker', 'presentation', 'event', 'answered_by', 'speaker')
    readonly_fields = ('created_at',)
    fieldsets = (
        (None, {
            'fields': ('event', 'presentation', 'asker', 'speaker', 'question_text')
        }),
        ('Ответ', {
            'fields': ('answered', 'answer_text', 'answered_by', 'answered_at')
        }),
    )

    def short_question(self, obj):
        return obj.question_text[:50] + '...' if len(obj.question_text) > 50 else obj.question_text
    short_question.short_description = 'Вопрос'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('presentation', 'asker', 'event')


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


@admin.register(SpeakerApplication)
class SpeakerApplicationAdmin(admin.ModelAdmin):
    list_display = ('user', 'topic', 'status', 'created_at')
    list_filter = ('status', 'created_at')