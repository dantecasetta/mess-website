from django.conf import settings
from django.db import models


class PersonalityQuiz(models.Model):
    LIKERT_CHOICES = [
        (1, '1'),
        (2, '2'),
        (3, '3'),
        (4, '4'),
        (5, '5'),
    ]

    # Personality questions
    QUESTIONS = [
        "Do you prefer going out (5) or staying in (1) on a friday night?",
        "Do you prefer Movies (5) or Books (1)?",
        "Are you Clingy (5) or not Clingy (1)?",
        "Do you prefer Beer (5) or Hot Chocolate (1)?",
        "Do you prefer Legos (5) or painting (1)?",
        "What do you think you GIVE more - princess treatment (5) or bare minimum (1)?",
        "Do you prefer spending your sunday hanging out with friends (5) or being by yourself (1)?",
        "Do you prefer Late night cuddles (5) or late night talks (1)?",
        "In public do you prefer Making out (5) or not touching (1)?",
    ]

    # Preset category groups by color with target weights for each category
    # Category 0: AntiSocial (1) -> Social (5)
    # Category 1: Books (1) -> Movies (5)  
    # Category 2: Less Romantic (1) -> More Romantic (5)
    CATEGORY_GROUPS = {
        'Purple': {'weights': [5.0, 5.0, 5.0], 'description': 'Social, Movies, More Romantic'},
        'red': {'weights': [3, 3, 3], 'description': 'Balanced'},
        'gray': {'weights': [1.0, 1.0, 1.0], 'description': 'AntiSocial, Books, Less Romantic'},
        'green': {'weights': [4.0, 2.0, 5.0], 'description': 'Social, Books, More Romantic'},
        'blue': {'weights': [5.0, 5.0, 1.0], 'description': 'Social, Movies, Less Romantic'},
        'pink': {'weights': [2.0, 1.0, 5.0], 'description': 'Moderate Social, Books, More Romantic'},
        'orange': {'weights': [1.0, 5.0, 1.0], 'description': 'AntiSocial, Movies, Less Romantic'},
        'beige': {'weights': [3.0, 4.0, 2], 'description': 'Moderate Social, Movies, Less Romantic'},
    }

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='personality_quiz'
    )

    # Stores answers to 9 questions as a JSON array
    # Index 0-2 contribute to category 0, 3-5 to category 1, 6-8 to category 2
    answers = models.JSONField(
        default=list,
        help_text="Array of 9 answers (1-5 Likert scale). Indices: [0,3,6]→cat0, [1,4,7]→cat1, [2,5,8]→cat2"
    )

    # Stores calculated weighted averages for each of 3 categories
    calculated_weights = models.JSONField(
        default=list,
        help_text="Array of 3 weighted averages corresponding to categories"
    )

    # Stores the category classification
    category_classification = models.CharField(
        max_length=20,
        blank=True,
        help_text="The category (category_0, category_1, category_2) that best matches the calculated weights"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Personality quiz for {self.user.username}"

    def calculate_weighted_averages(self):
        """
        Calculate 3 weighted averages from the answers array with custom weights per question.
        Category 0: answers[0]*0.3 + answers[3]*0.2 + answers[6]*0.5
        Category 1: answers[1]*(1/3) + answers[4]*(1/3) + answers[7]*(1/3) (equal weights)
        Category 2: answers[2]*0.6 + answers[5]*0.2 + answers[8]*0.2
        """
        if len(self.answers) < 9:
            raise ValueError("Answers array must contain at least 9 values")

        # Define weights for each category
        # Category 0: q0=0.3, q3=0.2, q6=0.5
        # Category 1: q1=1/3, q4=1/3, q7=1/3 (equal)
        # Category 2: q2=0.6, q5=0.2, q8=0.2
        weights = [
            [0.3, 0.2, 0.5],           # Category 0: indices [0, 3, 6]
            [1/3, 1/3, 1/3],           # Category 1: indices [1, 4, 7] (equal weights)
            [0.6, 0.2, 0.2],           # Category 2: indices [2, 5, 8]
        ]
        
        indices = [
            [0, 3, 6],                 # Category 0
            [1, 4, 7],                 # Category 1
            [2, 5, 8],                 # Category 2
        ]

        self.calculated_weights = []
        for category_idx, idx_list in enumerate(indices):
            weighted_sum = sum(self.answers[idx_list[i]] * weights[category_idx][i] for i in range(3))
            self.calculated_weights.append(round(weighted_sum, 2))

        return self.calculated_weights

    def classify_category(self):
        """
        Compare calculated weights to preset color groups and assign the best matching group.
        Uses Euclidean distance to find the closest match.
        """
        if not self.calculated_weights:
            self.calculate_weighted_averages()

        best_category = None
        best_distance = float('inf')

        for color_name, color_data in self.CATEGORY_GROUPS.items():
            target_weights = color_data['weights']
            
            # Calculate Euclidean distance between calculated weights and target weights
            distance = sum((self.calculated_weights[i] - target_weights[i]) ** 2 for i in range(3)) ** 0.5
            
            if distance < best_distance:
                best_distance = distance
                best_category = color_name

        self.category_classification = best_category
        return best_category

    def save(self, *args, **kwargs):
        """Override save to automatically calculate weights and classify category."""
        if self.answers and len(self.answers) >= 9:
            self.calculate_weighted_averages()
            self.classify_category()
        super().save(*args, **kwargs)


class AttractionQuiz(models.Model):
    """Quiz to determine what personality type a user is attracted to."""
    LIKERT_CHOICES = [
        (1, '1'),
        (2, '2'),
        (3, '3'),
        (4, '4'),
        (5, '5'),
    ]

    # Attraction preference questions - mirroring the 3 categories
    QUESTIONS = [
        "What do you find attractive: AntiSocial (1) or Social (5)?",
        "What do you find attractive: Books person (1) or Movies person (5)?",
        "What do you find attractive: Less Romantic (1) or More Romantic (5)?",
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='attraction_quiz'
    )

    # Stores answers to 3 questions as a JSON array
    answers = models.JSONField(
        default=list,
        help_text="Array of 3 answers (1-5 Likert scale) for attraction preferences"
    )

    # Stores calculated preferences for each of 3 categories
    preferences = models.JSONField(
        default=list,
        help_text="Array of 3 preference values corresponding to categories"
    )

    # Stores the personality category they're most attracted to
    most_attracted_category = models.CharField(
        max_length=20,
        blank=True,
        help_text="The personality category (color) they're most attracted to"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Attraction quiz for {self.user.username}"

    def calculate_preferences(self):
        """Calculate preference weights from the 3 answers."""
        if len(self.answers) < 3:
            raise ValueError("Answers array must contain at least 3 values")

        # Simply store the answers as preferences (1-5 scale)
        self.preferences = list(self.answers)
        return self.preferences

    def find_most_attracted_category(self):
        """
        Find which personality category is most aligned with attraction preferences.
        Uses Euclidean distance to find the closest match.
        """
        if not self.preferences:
            self.calculate_preferences()

        best_category = None
        best_distance = float('inf')

        # Use the same CATEGORY_GROUPS from PersonalityQuiz
        for color_name, color_data in PersonalityQuiz.CATEGORY_GROUPS.items():
            target_weights = color_data['weights']
            
            # Calculate Euclidean distance between preferences and target weights
            distance = sum((self.preferences[i] - target_weights[i]) ** 2 for i in range(3)) ** 0.5
            
            if distance < best_distance:
                best_distance = distance
                best_category = color_name

        self.most_attracted_category = best_category
        return best_category

    def save(self, *args, **kwargs):
        """Override save to automatically calculate preferences and find attracted category."""
        if self.answers and len(self.answers) >= 3:
            self.calculate_preferences()
            self.find_most_attracted_category()
            print(f"[DEBUG] AttractionQuiz: answers={self.answers}, preferences={self.preferences}, most_attracted_category={self.most_attracted_category}")
        super().save(*args, **kwargs)
