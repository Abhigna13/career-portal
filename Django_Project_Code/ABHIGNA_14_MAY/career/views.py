from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.utils.http import url_has_allowed_host_and_scheme

from .models import Skill, JobRole, Project, UserProfile


# HOME
def home(request):
    return render(request, 'home.html')

# REGISTER
def register_view(request):
    if request.method == 'POST':
        print("POST HIT")  # DEBUG

        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password1', '')
        confirm_password = request.POST.get('password2', '')

        if not username or not email or not password:
            messages.error(request, "All fields are required")
            return render(request, 'register.html')

        if password != confirm_password:
            messages.error(request, "Passwords do not match")
            return render(request, 'register.html')

        if len(password) < 6:
            messages.error(request, "Password must be at least 6 characters")
            return render(request, 'register.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return render(request, 'register.html')

        User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        messages.success(request, "Registration successful! Please login.")
        return redirect('login')

    return render(request, 'register.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        if not username or not password:
            messages.error(request, "Please enter username and password")
            return redirect('login')

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return redirect('skills')

        messages.error(request, "Invalid credentials")

    return render(request, 'login.html')


# JOB RECOMMENDATIONS
@login_required(login_url='/login/')
def job_recommendations_page(request):
    user_profile, _ = UserProfile.objects.get_or_create(user=request.user)

    user_skills = set(user_profile.skills.values_list('id', flat=True))

    jobs = JobRole.objects.prefetch_related('skills_required', 'projects')

    recommended_jobs = []

    for job in jobs:
        job_skill_ids = set(job.skills_required.values_list('id', flat=True))

        matching = user_skills.intersection(job_skill_ids)

        match_percent = int((len(matching) / len(job_skill_ids)) * 100) if job_skill_ids else 0

        missing_skills = job_skill_ids - user_skills

        projects = Project.objects.filter(skills__id__in=missing_skills).distinct()[:2]

        recommended_jobs.append({
            'job': job,
            'match': match_percent,
            'projects': projects,
        })

    return render(request, 'jobs.html', {'jobs': recommended_jobs})


# SKILLS PAGE
@login_required(login_url='/login/')
def skills_page(request):
    user_profile, _ = UserProfile.objects.get_or_create(user=request.user)

    # ADD SKILL
    if request.method == 'POST':
        new_skill = request.POST.get('new_skill', '').strip()
        if new_skill:
            skill_obj, _ = Skill.objects.get_or_create(name=new_skill)
            user_profile.skills.add(skill_obj)
            messages.success(request, f"{new_skill} added!")
        return redirect('skills')

    user_skills = user_profile.skills.all()
    user_skill_ids = set(user_skills.values_list('id', flat=True))

    jobs = JobRole.objects.prefetch_related('skills_required')

    total_match = 0
    count = 0
    missing_counter = {}

    for job in jobs:
        job_skills = set(job.skills_required.values_list('id', flat=True))
        if not job_skills:
            continue

        match = len(user_skill_ids & job_skills) / len(job_skills)
        total_match += match
        count += 1

        missing = job_skills - user_skill_ids
        for m in missing:
            missing_counter[m] = missing_counter.get(m, 0) + 1

    match_score = int((total_match / count) * 100) if count else 0

    # Next best skill
    next_skill = None
    if missing_counter:
        next_skill_id = max(missing_counter, key=missing_counter.get)
        next_skill = Skill.objects.get(id=next_skill_id)

    # Recommendations
    recommended_skills = Skill.objects.filter(id__in=missing_counter.keys())[:3]

    # Insights
    insights = []
    for skill in Skill.objects.all():
        job_count = JobRole.objects.filter(skills_required=skill).count()
        if job_count > 0:
            insights.append((skill.name, job_count))

    return render(request, 'skills.html', {
        'user_skills': user_skills,
        'match_score': match_score,
        'next_skill': next_skill,
        'recommended_skills': recommended_skills,
        'insights': insights[:3],
    })

# DASHBOARD
def dashboard(request):
    return redirect('job_recommendations')


# LOGOUT
def logout_view(request):
    logout(request)
    messages.success(request, "Logged out successfully")
    return redirect('login')