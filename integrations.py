from django import forms
from django.urls import reverse
from django.utils import timezone
from django.utils.html import format_html, format_html_join
from django.utils.translation import ugettext_lazy

from admin_notes.models import AdminNote


class AdminNotesInlineFormMixin(forms.ModelForm):
    new_admin_note = forms.CharField(
        label=ugettext_lazy('Add admin note'),
        required=False,
        widget=forms.Textarea(attrs={'rows': 3}),
        help_text=ugettext_lazy('Adds a new append-only note. Existing notes are read-only.'),
    )


class AdminNotesProfileInlineMixin:
    admin_notes_target_user_attr = 'user'
    admin_notes_legacy_field = 'admin_notes'
    admin_notes_history_limit = 25
    admin_notes_history_title = 'Admin note history (newest first)'
    admin_notes_legacy_title = 'Legacy admin notes (historical, read-only)'

    def _get_admin_notes_target_user(self, obj):
        return getattr(obj, self.admin_notes_target_user_attr, None)

    def _get_admin_notes_legacy_value(self, obj):
        legacy_field = self.admin_notes_legacy_field
        if not legacy_field:
            return ''
        return getattr(obj, legacy_field, '')

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(super().get_readonly_fields(request, obj))
        if self.admin_notes_legacy_field:
            readonly_fields.append('legacy_admin_notes')
        readonly_fields.append('admin_note_history')
        return tuple(dict.fromkeys(readonly_fields))

    def get_exclude(self, request, obj=None):
        exclude = list(super().get_exclude(request, obj) or [])
        if self.admin_notes_legacy_field:
            exclude.append(self.admin_notes_legacy_field)
        return tuple(dict.fromkeys(exclude))

    def legacy_admin_notes(self, obj):
        legacy_value = self._get_admin_notes_legacy_value(obj)
        if not obj or not legacy_value:
            return '-'
        return format_html('<div style="white-space: pre-wrap;">{}</div>', legacy_value)

    legacy_admin_notes.short_description = admin_notes_legacy_title

    def admin_note_history(self, obj):
        if not obj:
            return '-'

        target_user = self._get_admin_notes_target_user(obj)
        if target_user is None:
            return '-'

        notes = AdminNote.objects.filter(user=target_user).select_related('created_by')[: self.admin_notes_history_limit]
        if not notes:
            return '-'

        rendered_notes = format_html_join(
            '',
            '<li><strong>{}</strong> [{}]<br>{}<br><a href="{}">Delete</a></li>',
            (
                (
                    timezone.localtime(note.created_at).strftime('%Y-%m-%d %H:%M'),
                    note.created_by.username if note.created_by else 'system',
                    note.text,
                    reverse('admin:admin_notes_adminnote_delete', args=[note.id]),
                )
                for note in notes
            ),
        )
        return format_html('<ol>{}</ol>', rendered_notes)

    admin_note_history.short_description = admin_notes_history_title


class AdminNotesUserAdminMixin:
    admin_notes_field_name = 'new_admin_note'
    admin_notes_target_user_attr = 'user'

    def _get_admin_notes_target_user(self, inline_instance):
        return getattr(inline_instance, self.admin_notes_target_user_attr, None)

    def save_formset(self, request, form, formset, change):
        super().save_formset(request, form, formset, change)

        for inline_form in formset.forms:
            cleaned_data = getattr(inline_form, 'cleaned_data', None)
            if not cleaned_data or cleaned_data.get('DELETE'):
                continue

            note_text = (cleaned_data.get(self.admin_notes_field_name) or '').strip()
            if not note_text:
                continue

            target_user = self._get_admin_notes_target_user(inline_form.instance)
            if target_user is None:
                continue

            AdminNote.objects.create(user=target_user, text=note_text, created_by=request.user)
