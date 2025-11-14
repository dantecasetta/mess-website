from django import forms
from .models import PersonalityQuiz


class PersonalityQuizForm(forms.ModelForm):
    class Meta:
        model = PersonalityQuiz
        fields = [
            'q1_romantic',
            'q2_outgoing',
            'q3_deep_talks',
            'q4_planner',
            'q5_spontaneous',
        ]
        widgets = {
            'q1_romantic': forms.RadioSelect,
            'q2_outgoing': forms.RadioSelect,
            'q3_deep_talks': forms.RadioSelect,
            'q4_planner': forms.RadioSelect,
            'q5_spontaneous': forms.RadioSelect,
        }
