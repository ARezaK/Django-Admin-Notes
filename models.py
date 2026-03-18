from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy


class AdminNote(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=ugettext_lazy('User'),
        related_name='received_admin_notes',
        on_delete=models.CASCADE,
    )
    text = models.TextField(verbose_name=ugettext_lazy('Text'))
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=ugettext_lazy('Created By'),
        related_name='created_admin_notes',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    created_at = models.DateTimeField(verbose_name=ugettext_lazy('Created At'), auto_now_add=True)

    def __str__(self):
        return f'Admin note for {self.user}'

    class Meta:
        ordering = ['-created_at', '-id']
        verbose_name = ugettext_lazy('Admin Note')
        verbose_name_plural = ugettext_lazy('Admin Notes')
