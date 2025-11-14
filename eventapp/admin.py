from django.contrib import admin
from .models import PersonalityQuiz, MatchResult
from .models import CheckIn 

admin.site.register(PersonalityQuiz)
admin.site.register(MatchResult)

@admin.register(CheckIn)
class CheckInAdmin(admin.ModelAdmin):
    list_display = ('user', 'checked_in_at')