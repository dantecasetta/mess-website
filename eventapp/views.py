from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages

from .forms import PersonalityQuizForm
from .models import PersonalityQuiz, MatchResult

from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from .models import MatchResult, CheckIn   # make sure these are imported

def home(request):
    return render(request, 'home.html')  # you already have this template


def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()     # create user
            login(request, user)   # log them in immediately
            return redirect('dashboard')
    else:
        form = UserCreationForm()

    return render(request, 'signup.html', {'form': form})


@login_required
def dashboard(request):
    user = request.user

    # Has this user done the quiz?
    has_quiz = PersonalityQuiz.objects.filter(user=user).exists()

    # Get this user's top 3 matches
    matches = MatchResult.objects.filter(user=user).order_by('rank')[:3]
    has_matches = matches.exists()

    # Build data for lights: for each match, is that person checked in?
    match_statuses = []
    for result in matches:
        is_checked_in = CheckIn.objects.filter(user=result.match).exists()
        match_statuses.append({
            'result': result,          # the MatchResult object
            'is_checked_in': is_checked_in,  # bool
        })

    context = {
        'has_quiz': has_quiz,
        'has_matches': has_matches,
        'matches': matches,
        'match_statuses': match_statuses,
    }

    return render(request, 'dashboard.html', context)

    context = {
        'match_statuses': match_statuses,
    }
    return render(request, 'dashboard.html', context)


def logout_view(request):
    logout(request)          # clears the session; logs the user out
    return redirect('home')  # send them back to the home page


@login_required
def personality_quiz_view(request):
    # Check if the user has already submitted the quiz
    try:
        existing_quiz = request.user.personality_quiz
    except PersonalityQuiz.DoesNotExist:
        existing_quiz = None

    if existing_quiz is not None:
        # User already submitted; do not let them submit again
        messages.info(request, "You’ve already submitted the personality quiz. You can only do it once.")
        return redirect('dashboard')

    if request.method == 'POST':
        form = PersonalityQuizForm(request.POST)
        if form.is_valid():
            quiz = form.save(commit=False)
            quiz.user = request.user
            quiz.save()
            messages.success(request, "Your personality quiz has been saved!")
            return redirect('dashboard')
    else:
        form = PersonalityQuizForm()

    return render(request, 'personality_quiz.html', {'form': form})


@login_required
def event_view(request):
    matches = MatchResult.objects.filter(user=request.user).order_by('rank')[:3]

    match_statuses = []
    for m in matches:
        is_checked_in = CheckIn.objects.filter(user=m.match).exists()
        match_statuses.append({
            'match': m,
            'is_checked_in': is_checked_in,
        })

    return render(request, 'event.html', {'match_statuses': match_statuses})