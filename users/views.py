from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST, require_GET
import json
from rest_framework import status

from skills.models import Skill
from team_finder.constants import SKILL_NUM
from team_finder.service import paginator_get_page
from users.forms import RegisterForm, LoginForm
from users.forms import EditProfileForm, ChangePasswordForm
from users.models import User


def register_view(request):
    form = RegisterForm(request.POST or None)
    if form.is_valid():
        user = form.save()
        login(request, user)
        return redirect('project_list')
    else:
        form = RegisterForm()
    return render(request, 'users/register.html', {'form': form})


def login_view(request):
    form = LoginForm(data=request.POST or None)
    if form.is_valid():
        login(request, form.get_user())
        return redirect('project_list')
    else:
        form = LoginForm()
    return render(request, 'users/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('project_list')


def user_detail(request, user_id):
    profile_user = get_object_or_404(User, pk=user_id)
    return render(request, 'users/user-details.html', {'user': profile_user})


@login_required
def edit_profile(request):
    form = EditProfileForm(
        request.POST or None,
        request.FILES,
        instance=request.user
        )
    if form.is_valid():
        form.save()
        return redirect('users:user_detail', user_id=request.user.pk)
    else:
        form = EditProfileForm(instance=request.user)
    return render(request, 'users/edit_profile.html', {'form': form})


@login_required
def change_password(request):
    form = ChangePasswordForm(
        request.user,
        data=request.POST or None)
    if form.is_valid():
        form.save()
        update_session_auth_hash(request, request.user)
        return redirect('users:user_detail', user_id=request.user.pk)
    else:
        form = ChangePasswordForm(request.user)
    return render(request, 'users/change_password.html', {'form': form})


def user_list(request):
    users = User.objects.all()
    active_skill = None
    all_skills = Skill.objects.all()

    skill_name = request.GET.get('skill')
    if skill_name:
        users = users.filter(skills__name=skill_name).distinct()
        active_skill = skill_name

    page_obj = paginator_get_page(objects=users, request=request)
    context = {
        'participants': page_obj,
        'all_skills': all_skills,
        'active_skill': active_skill,
    }
    return render(request, 'users/participants.html', context)


@require_GET
def skills_autocomplete(request):
    query = request.GET.get('q', '').strip()
    if not query:
        return JsonResponse([], safe=False)
    skills = Skill.objects.filter(
        name__istartswith=query
        ).order_by('name')[:SKILL_NUM]
    skills_data = [{'id': skill.id, 'name': skill.name} for skill in skills]
    return JsonResponse(skills_data, safe=False)


@require_POST
@login_required
def add_skill(request, user_id):
    if request.user.pk != user_id:
        return JsonResponse(
            {'error': 'Нет прав'},
            status=status.HTTP_403_FORBIDDEN
            )

    data = json.loads(request.body)
    skill_id = data.get('skill_id')
    name = data.get('name')
    created = False
    added = False

    if skill_id:
        skill = get_object_or_404(Skill, pk=skill_id)
    elif name:
        skill, created = Skill.objects.get_or_create(name=name.strip())
    else:
        return JsonResponse({'error': 'Не переданы параметры'}, status=400)

    user = request.user
    if not user.skills.filter(pk=skill.pk).exists():
        user.skills.add(skill)
        added = True

    return JsonResponse({
        'id': skill.id,
        'name': skill.name,
        'created': created,
        'added': added,
    })


@require_POST
@login_required
def remove_skill(request, user_id, skill_id):
    if request.user.pk != user_id:
        return JsonResponse({'error': 'Нет прав'}, status=403)
    user = request.user
    skill = get_object_or_404(Skill, pk=skill_id)
    if user.skills.filter(pk=skill.pk).exists():
        user.skills.remove(skill)
        return JsonResponse({'status': 'ok'})
    return JsonResponse(
        {'status': 'error', 'detail': 'Навык не найден у пользователя'}
        )
