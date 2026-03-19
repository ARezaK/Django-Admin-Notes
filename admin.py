from django.contrib import admin

from admin_notes.models import AdminNote


@admin.register(AdminNote)
class AdminNoteAdmin(admin.ModelAdmin):
    list_display = ('user', 'note_preview')
    search_fields = ('text', 'user__username')
    list_filter = ('created_by', 'created_at')
    ordering = ('-id',)
    date_hierarchy = 'created_at'
    actions = None

    def note_preview(self, obj):
        return obj.text[:100]

    note_preview.short_description = 'Text'

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        if obj is None:
            return super().has_change_permission(request, obj)
        return False
