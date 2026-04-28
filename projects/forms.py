from django import forms

from team_finder.service import form_clean_github_url
from projects.models import Project


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'description', 'github_url', 'status']
        widgets = {
            'status': forms.Select(choices=Project.Status.choices),
            'description': forms.Textarea(attrs={'rows': 4}),
        }
        labels = {
            'name': 'Название',
            'description': 'Описание',
            'github_url': 'Ссылка на GitHub',
            'status': 'Статус',
        }

    def clean_github_url(self):
        return form_clean_github_url(self)
