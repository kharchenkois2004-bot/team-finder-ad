from django.db.models import Count
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from team_finder.service import paginator_get_page
from projects.models import Project
from projects.forms import ProjectForm


def project_list(request):
    projects = Project.objects.select_related('owner').annotate(
        participants_count=Count('participants')
    ).order_by('-created_at')
    page_obj = paginator_get_page(objects=projects, request=request)
    return render(
        request,
        'projects/project_list.html',
        {'projects': page_obj}
        )


def project_detail(request, project_id):
    project = get_object_or_404(
        Project.objects.select_related('owner'),
        pk=project_id
        )
    return render(
        request,
        'projects/project-details.html',
        {'project': project}
        )


@login_required
def project_create(request):
    form = ProjectForm(request.POST or None)
    if form.is_valid():
        project = form.save(commit=False)
        project.owner = request.user
        project.save()
        form.save_m2m()
        project.participants.add(request.user)
        return redirect('project_detail', project_id=project.pk)
    else:
        form = ProjectForm()
    return render(
        request,
        'projects/create-project.html',
        {'form': form, 'is_edit': False}
        )


@login_required
def project_edit(request, project_id):
    project = get_object_or_404(
        Project,
        pk=project_id,
        owner=request.user
        )
    form = ProjectForm(
        request.POST or None,
        instance=project
        )
    if form.is_valid():
        form.save()
        return redirect('project_detail', project_id=project.pk)
    else:
        form = ProjectForm(instance=project)
    return render(
        request,
        'projects/create-project.html',
        {'form': form, 'is_edit': True}
        )


@require_POST
@login_required
def project_complete(request, project_id):
    project = get_object_or_404(
        Project,
        pk=project_id,
        owner=request.user,
        status=Project.Status.OPEN
        )
    project.status = Project.Status.CLOSED
    project.save()
    return JsonResponse({'status': 'ok', 'project_status': 'closed'})


@require_POST
@login_required
def toggle_participate(request, project_id):
    project = get_object_or_404(
        Project,
        pk=project_id
        )
    if not_participant := project.participants.filter(
         pk=request.user.pk).exists():
        project.participants.remove(request.user)
    else:
        project.participants.add(request.user)
    return JsonResponse({'status': 'ok', 'participated': not not_participant})


@require_POST
@login_required
def toggle_favorite(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    user = request.user
    if not_favorited := user.favorites.filter(pk=project.pk).exists():
        user.favorites.remove(project)
    else:
        user.favorites.add(project)
    return JsonResponse({
        'status': 'ok',
        'favorited': not_favorited
    })
