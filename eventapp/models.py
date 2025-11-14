from django.conf import settings
from django.db import models


class PersonalityQuiz(models.Model):
    LIKERT_CHOICES = [
        (1, 'Strongly disagree'),
        (2, 'Disagree'),
        (3, 'Neutral'),
        (4, 'Agree'),
        (5, 'Strongly agree'),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='personality_quiz'
    )

    # Example questions – you can rename/change these later
    q1_romantic = models.IntegerField(
        choices=LIKERT_CHOICES,
        verbose_name="I enjoy romantic gestures"
    )
    q2_outgoing = models.IntegerField(
        choices=LIKERT_CHOICES,
        verbose_name="I like going to parties and social events"
    )
    q3_deep_talks = models.IntegerField(
        choices=LIKERT_CHOICES,
        verbose_name="I prefer deep conversations over small talk"
    )
    q4_planner = models.IntegerField(
        choices=LIKERT_CHOICES,
        verbose_name="I like to plan things in advance"
    )
    q5_spontaneous = models.IntegerField(
        choices=LIKERT_CHOICES,
        verbose_name="I enjoy spontaneous adventures"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Personality quiz for {self.user.username}"

class MatchResult(models.Model):
    """
    Precomputed matches for a user.
    Example: 3 rows per user for their top 3 matches.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='my_matches'
    )
    match = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='matched_by'
    )
    score = models.FloatField(help_text="Similarity score or compatibility score")
    rank = models.PositiveSmallIntegerField(help_text="1 = best match, 2 = second, etc.")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'rank')
        ordering = ['rank']

    def __str__(self):
        return f"{self.user.username} → {self.match.username} (rank {self.rank})"
    
    from django.db import models
from django.contrib.auth.models import User

class CheckIn(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='checkin'
    )
    checked_in_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} checked in at {self.checked_in_at}"
