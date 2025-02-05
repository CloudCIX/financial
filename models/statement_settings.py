# libs
from django.db import models
from django.urls import reverse


__all__ = [
    'StatementSettings',
]


class StatementSettings(models.Model):
    """
    The StatementSettings model represents the data that determines if and when a statement is sent to a
    partner's address.
    """
    address_id = models.IntegerField(primary_key=True)
    day = models.JSONField(default=list)
    min_credit = models.DecimalField(decimal_places=4, max_digits=18, null=True)
    min_debit = models.DecimalField(decimal_places=4, max_digits=18, null=True)
    reply_to = models.TextField(null=True)
    signature = models.TextField(default='')

    class Meta:
        """
        Metadata about the model for Django to use in whatever way it sees fit
        """
        db_table = 'statement_settings'
        ordering = ['address_id']

        indexes = [
            # Indexing everything in the `search_fields` map in List Controller
            models.Index(fields=['address_id'], name='statement_settings_address_id'),
            models.Index(fields=['day'], name='statement_settings_day'),
            models.Index(fields=['min_credit'], name='statement_settings_min_credit'),
            models.Index(fields=['min_debit'], name='statement_settings_min_debit'),
        ]

    def get_absolute_url(self) -> str:
        """
        Generates the absolute URL that corresponds to the StatementSettingsResource view for this Statement Settings
        record
        :return: A URL that corresponds to the views for this Statement Settings record
        """
        return reverse('statement_settings_resource', kwargs={'pk': self.address_id})
