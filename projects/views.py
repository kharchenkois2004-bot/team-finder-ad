from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Project
from .forms import ProjectForm

ITEMS_PER_PAGE = 12


def project_list(request):
    projects = Project.objects.all()
    paginator = Paginator(
        projects,
        ITEMS_PER_PAGE
        )
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(
        request,
        'projects/project_list.html',
        {'projects': page_obj}
        )


def project_detail(request, project_id):
    project = get_object_or_404(
        Project,
        pk=project_id
        )
    return render(
        request,
        'projects/project-details.html',
        {'project': project}
        )


@login_required
def project_create(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
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
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
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
    if project.participants.filter(pk=request.user.pk).exists():
        project.participants.remove(request.user)
        participated = False
    else:
        project.participants.add(request.user)
        participated = True
    return JsonResponse({'status': 'ok', 'participated': participated})


@require_POST
@login_required
def toggle_favorite(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    user = request.user
    if user.favorites.filter(pk=project.pk).exists():
        user.favorites.remove(project)
        favorited = False
    else:
        user.favorites.add(project)
        favorited = True
    return JsonResponse({
        'status': 'ok',
        'favorited': favorited
    })
