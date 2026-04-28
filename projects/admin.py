from django.contrib import admin
from .models import Project


class ProjectAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'owner',
        'status',
        'created_at',
        'participants_count'
        )
    list_filter = (
        'status',
        'created_at'
        )
    search_fields = (
        'name',
        'owner__email',
        'owner__name',
        'owner__surname'
        )
    ordering = ('-created_at',)
    filter_horizontal = ('participants',)
    readonly_fields = ('created_at',)

    def participants_count(self, obj):
        return obj.participants.count()
    participants_count.short_description = 'Кол-во участников'


admin.site.register(Project, ProjectAdmin)
