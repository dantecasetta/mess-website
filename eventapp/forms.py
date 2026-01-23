from django import forms
from .models import PersonalityQuiz, AttractionQuiz


class PersonalityQuizForm(forms.Form):
    """Form for collecting personality quiz answers as a 1-5 Likert scale."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Dynamically create fields for each question
        for i, question in enumerate(PersonalityQuiz.QUESTIONS):
            self.fields[f'q{i}'] = forms.ChoiceField(
                label=question,
                choices=PersonalityQuiz.LIKERT_CHOICES,
                widget=forms.RadioSelect,
                required=True
            )
    
    def get_answers(self):
        """Extract answers as an array in the correct order."""
        answers = []
        for i in range(len(PersonalityQuiz.QUESTIONS)):
            answer = self.cleaned_data.get(f'q{i}')
            if answer:
                answers.append(int(answer))
        return answers


class AttractionQuizForm(forms.Form):
    """Form for collecting attraction preferences as a 1-5 Likert scale."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Dynamically create fields for each question
        for i, question in enumerate(AttractionQuiz.QUESTIONS):
            self.fields[f'q{i}'] = forms.ChoiceField(
                label=question,
                choices=AttractionQuiz.LIKERT_CHOICES,
                widget=forms.RadioSelect,
                required=True
            )
    
    def get_answers(self):
        """Extract answers as an array in the correct order."""
        answers = []
        for i in range(len(AttractionQuiz.QUESTIONS)):
            answer = self.cleaned_data.get(f'q{i}')
            if answer:
                answers.append(int(answer))
        return answers
