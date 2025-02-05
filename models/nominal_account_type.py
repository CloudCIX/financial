# libs
from cloudcix_rest.models import BaseModel
from django.db import models


__all__ = [
    'NominalAccountType',
]


class NominalAccountType(BaseModel):
    """
    The Nominal Account Type model represents what kind of transactions will be recorded in a Nominal Account. Examples
    include 'Fixed Assets', 'Current Liabilities', etc.
    """
    description = models.CharField(max_length=25)
    max_account_number = models.IntegerField()
    min_account_number = models.IntegerField()

    class Meta:
        """
        Metadata about the model for Django to use in whatever way it sees fit
        """
        db_table = 'nominal_account_type'

        indexes = [
            # Indexing everything in the `search_fields` map in List Controller
            models.Index(fields=['id'], name='account_type_id'),
            models.Index(fields=['deleted'], name='account_type_deleted'),
            models.Index(fields=['description'], name='account_type_description'),
            models.Index(fields=['min_account_number'], name='account_type_min_acc_number'),
        ]
        ordering = ['description']
