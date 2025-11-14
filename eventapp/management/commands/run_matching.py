from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from eventapp.models import PersonalityQuiz, MatchResult


class Command(BaseCommand):
    help = "Compute top 3 matches for each user based on personality quiz answers."

    def handle(self, *args, **options):
        User = get_user_model()

        quizzes = list(PersonalityQuiz.objects.select_related('user'))

        if len(quizzes) < 2:
            self.stdout.write(self.style.WARNING(
                "Not enough quiz responses (need at least 2 users). No matches computed."
            ))
            return

        # Clear all existing match results (fresh recompute)
        MatchResult.objects.all().delete()
        self.stdout.write("Cleared existing MatchResult entries.")

        # Build vectors: user_id -> list of answers
        user_vectors = {}
        for quiz in quizzes:
            user_vectors[quiz.user_id] = [
                quiz.q1_romantic,
                quiz.q2_outgoing,
                quiz.q3_deep_talks,
                quiz.q4_planner,
                quiz.q5_spontaneous,
            ]

        # For each user, compute similarity with everyone else
        for quiz in quizzes:
            user = quiz.user
            user_vec = user_vectors[user.id]

            scores = []

            for other_quiz in quizzes:
                other_user = other_quiz.user
                if other_user.id == user.id:
                    continue  # skip self

                other_vec = user_vectors[other_user.id]

                # Simple distance: sum of absolute differences
                distance = sum(
                    abs(a - b) for a, b in zip(user_vec, other_vec)
                )

                # Max possible distance per question is 4 (1..5), so:
                max_distance = 4 * len(user_vec)
                similarity = max_distance - distance  # higher = more similar

                scores.append((other_user, similarity))

            # Sort by similarity (highest first)
            scores.sort(key=lambda tup: tup[1], reverse=True)

            # Take top 3 matches
            top_matches = scores[:3]

            # Create MatchResult rows
            for rank_index, (match_user, similarity) in enumerate(top_matches, start=1):
                MatchResult.objects.create(
                    user=user,
                    match=match_user,
                    score=similarity,
                    rank=rank_index,
                )

            self.stdout.write(
                f"Computed {len(top_matches)} matches for {user.username}."
            )

        self.stdout.write(self.style.SUCCESS("Matching complete!"))
