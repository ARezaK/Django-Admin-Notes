# admin_notes

Reusable Django app for internal append-only admin notes on users.

## What this app provides

- `AdminNote` model:
  - `user` (target user)
  - `text`
  - `created_by` (staff/system user, nullable)
  - `created_at`
- Django admin list view with:
  - text search
  - filter by date
  - newest-first ordering
  - add/edit blocked from list/change UI
  - delete allowed when user has admin delete permission
- Reusable admin integration helpers for User admin pages:
  - `AdminNotesInlineFormMixin`
  - `AdminNotesProfileInlineMixin`
  - `AdminNotesUserAdminMixin`
  - `AdminNotesDirectUserAdminMixin`

## Files

- `admin_notes/models.py`
- `admin_notes/admin.py`
- `admin_notes/apps.py`
- `admin_notes/migrations/0001_initial.py`

## Install in another project

1. Copy the `admin_notes/` directory into the target project.
2. Add `'admin_notes'` to `INSTALLED_APPS`.
3. Run migrations:
   - `python manage.py migrate admin_notes`
4. Add note writes in your code paths, for example:
   - `AdminNote.objects.create(user=target_user, text="...", created_by=request.user)`
5. Wire User admin integration (pick one of the examples below).

## Explicit mixin examples

### Example A: Custom `UserProfile` inline with legacy field

Use this when your profile model has a historical text column like `admin_notes`.

```python
from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.auth.models import User

from admin_notes.integrations import (
    AdminNotesInlineFormMixin,
    AdminNotesProfileInlineMixin,
    AdminNotesUserAdminMixin,
)
from yourapp.models import UserProfile


class UserProfileInline(AdminNotesProfileInlineMixin, admin.StackedInline):
    class Form(AdminNotesInlineFormMixin, forms.ModelForm):
        class Meta:
            model = UserProfile
            fields = "__all__"

    model = UserProfile
    form = Form
    can_delete = False
    max_num = 1
    admin_notes_legacy_field = "admin_notes"   # show old notes as read-only
    admin_notes_target_user_attr = "user"      # how inline maps to auth user
    admin_notes_history_limit = 25


class UserAdmin(AdminNotesUserAdminMixin, DjangoUserAdmin):
    inlines = [UserProfileInline]


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
```

### Example B: Custom `UserProfile` inline without legacy field

Use this when you only want new `AdminNote` entries and no old text field.

```python
class UserProfileInline(AdminNotesProfileInlineMixin, admin.StackedInline):
    class Form(AdminNotesInlineFormMixin, forms.ModelForm):
        class Meta:
            model = UserProfile
            fields = "__all__"

    model = UserProfile
    form = Form
    can_delete = False
    max_num = 1
    admin_notes_legacy_field = None            # hide legacy notes block
    admin_notes_target_user_attr = "user"
```

### Example C: No profile model, direct `UserAdmin` integration (simple)

Use this when you want one write-only "Add admin note" field on the user admin page and no inline/history UI.

```python
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.auth.models import User

from admin_notes.integrations import AdminNotesDirectUserAdminMixin


class UserAdmin(AdminNotesDirectUserAdminMixin, DjangoUserAdmin):
    list_display = ('username', 'email', 'is_staff', 'is_active')
    search_fields = ('username', 'email')

    # Optional customization:
    # admin_notes_field_name = 'internal_note'
    # admin_notes_fieldset_title = 'Internal Notes'
    # admin_notes_target_user_attr = None  # default: note user is obj itself


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
```

How this works:
- Adds a write-only textarea field to the user edit form.
- On save, creates an `AdminNote` row if text was entered.
- Leaves note history to `/admin/admin_notes/adminnote/` list page.

## Writing notes in views/services

Use this pattern anywhere in your app:

```python
from admin_notes.models import AdminNote

AdminNote.objects.create(
    user=target_user,
    text="Sent warning for outside payment",
    created_by=request.user,  # or None for system/automation
)
```

If your project has a helper like `profile.add_admin_note(...)`, keep that helper thin and call `AdminNote.objects.create(...)` inside it.

## Delete behavior

- Delete links shown in inline history go to Django admin delete page for `AdminNote`.
- Deleting requires normal Django admin delete permission for `admin_notes.AdminNote`.


Example install from Git:

`pip install "git+ssh://git@github.com/<org>/<repo>.git@main#subdirectory=admin_notes"`

`django-admin-notes @ git+https://github.com/ARezaK/Django-Admin-Notes.git`

## Compatibility

- Built against Django 3.2 patterns used in this codebase.
- Uses `ugettext_lazy` to match existing translation style.
