from django.contrib import admin

from admin_notes.models import AdminNote


@admin.register(AdminNote)
class AdminNoteAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_by', 'created_at', 'note_preview')
    search_fields = ('text', 'user__username')
    list_filter = ('created_at',)
    ordering = ('-created_at', '-id')
    list_per_page = 20
    show_full_result_count = False
    list_select_related = ('user', 'created_by')
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
