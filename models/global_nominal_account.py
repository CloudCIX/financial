# stdlib
from datetime import datetime
# libs
from cloudcix_rest.models import BaseManager, BaseModel
from django.db import models
from django.urls import reverse
# local
from .nominal_account_type import NominalAccountType


__all__ = [
    'GlobalNominalAccount',
]


class GlobalNominalAccountManager(BaseManager):
    """
    Manager for Global Nominal Account which pre-fetches foreign keys
    """

    def get_queryset(self) -> models.QuerySet:
        """
        Extend the BaseManager QuerySet to prefetch all related data in every query to speed up serialization
        :return: A base queryset which can be further extended but always pre-fetches necessary data
        """
        return super().get_queryset().select_related(
            'nominal_account_type',
        )


class GlobalNominalAccount(BaseModel):
    """
    A Nominal Account stores accounting transactions for a fiscal year. Each Member gets a default set of accounts
    which can be updated and/or extended manually.
    """
    currency_id = models.IntegerField()
    description = models.CharField(max_length=100)
    external_reference = models.CharField(max_length=50, null=True)
    member_id = models.IntegerField()
    nominal_account_number = models.IntegerField()
    nominal_account_type = models.ForeignKey(NominalAccountType, models.CASCADE)
    valid_sales_account = models.BooleanField()
    valid_purchases_account = models.BooleanField()

    objects = GlobalNominalAccountManager()

    class Meta:
        """
        Metadata about the model for Django to use in whatever way it sees fit
        """
        db_table = 'global_nominal_account'

        indexes = [
            # Indexing everything in the `search_fields` map in List Controller
            models.Index(fields=['id'], name='global_account_id'),
            models.Index(fields=['deleted'], name='global_account_deleted'),
            models.Index(fields=['description'], name='global_account_description'),
            models.Index(fields=['external_reference'], name='global_account_external_ref'),
            models.Index(fields=['nominal_account_number'], name='global_account_number'),
        ]
        ordering = ['description']

    def get_absolute_url(self) -> str:
        """
        Generates the absolute URL that corresponds to the GlobalNominalAccountResource view for this Global Nominal
        Account record
        :return: A URL that corresponds to the views for this Global Nominal Account record
        """
        return reverse('global_nominal_account_resource', kwargs={'pk': self.pk})

    def set_deleted(self):
        deltime = datetime.utcnow().isoformat()
        self.deleted = deltime
        self.save()
        self.address_nominal_accounts.update(deleted=deltime)
