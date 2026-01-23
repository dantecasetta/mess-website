from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages

from .forms import PersonalityQuizForm, AttractionQuizForm
from .models import PersonalityQuiz, AttractionQuiz

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

    # Has this user done the personality quiz?
    has_quiz = PersonalityQuiz.objects.filter(user=user).exists()
    
    # Get the user's category classification
    category = None
    calculated_weights = None
    try:
        quiz = user.personality_quiz
        category = quiz.category_classification
        calculated_weights = quiz.calculated_weights
    except PersonalityQuiz.DoesNotExist:
        pass

    # Has this user done the attraction quiz?
    has_attraction_quiz = AttractionQuiz.objects.filter(user=user).exists()
    
    # Get the user's attraction preferences
    attracted_category = None
    try:
        attraction_quiz = user.attraction_quiz
        attracted_category = attraction_quiz.most_attracted_category
    except AttractionQuiz.DoesNotExist:
        pass

    context = {
        'has_quiz': has_quiz,
        'category': category,
        'calculated_weights': calculated_weights,
        'has_attraction_quiz': has_attraction_quiz,
        'attracted_category': attracted_category,
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
            # Extract answers from the form
            answers = form.get_answers()
            
            # Create the PersonalityQuiz object with the answers
            quiz = PersonalityQuiz(user=request.user, answers=answers)
            quiz.save()  # This will auto-calculate weights and classify
            
            messages.success(request, "Your personality quiz has been saved!")
            return redirect('dashboard')
    else:
        form = PersonalityQuizForm()

    return render(request, 'personality_quiz.html', {'form': form})


@login_required
def attraction_quiz_view(request):
    # Check if the user has already submitted the attraction quiz
    try:
        existing_quiz = request.user.attraction_quiz
    except AttractionQuiz.DoesNotExist:
        existing_quiz = None

    if existing_quiz is not None:
        # User already submitted; do not let them submit again
        messages.info(request, "You've already submitted the attraction quiz. You can only do it once.")
        return redirect('dashboard')

    if request.method == 'POST':
        form = AttractionQuizForm(request.POST)
        if form.is_valid():
            # Extract answers from the form
            answers = form.get_answers()
            
            # Create the AttractionQuiz object with the answers
            quiz = AttractionQuiz(user=request.user, answers=answers)
            quiz.save()  # This will auto-calculate preferences and find attracted category
            
            messages.success(request, "Your attraction preferences have been saved!")
            return redirect('dashboard')
    else:
        form = AttractionQuizForm()

    return render(request, 'attraction_quiz.html', {'form': form})