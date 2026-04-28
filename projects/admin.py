from django.contrib import admin

from projects.models import Project


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'owner',
        'status',
        'created_at',
        'participants_count'
        )
    list_display_links = ('name',)
    list_editable = ('status',)
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
    filter_horizontal = ('participants',)
    readonly_fields = ('created_at',)

    @admin.display(description='Кол-во участников')
    def participants_count(self, obj):
        return obj.participants.count()
