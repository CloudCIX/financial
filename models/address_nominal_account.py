# libs
from cloudcix_rest.models import BaseManager, BaseModel
from django.db import models
# local
from .global_nominal_account import GlobalNominalAccount


__all__ = [
    'AddressNominalAccount',
]


class AddressNominalAccountManager(BaseManager):
    """
    Manager for Address Nominal Account which pre-fetches foreign keys
    """

    def get_queryset(self) -> models.QuerySet:
        """
        Extend the BaseManager QuerySet to prefetch all related data in every query to speed up serialization
        :return: A base queryset which can be further extended but always prefetches necessary data
        """
        return super().get_queryset().select_related(
            'global_nominal_account',
            'global_nominal_account__nominal_account_type',
        )


class AddressNominalAccount(BaseModel):
    """
    The Address Nominal Account model represents the Nominal Accounts that an Address inherits from its Member. The
    Member's Nominal Accounts can be customized for different Addresses.
    """
    address_id = models.IntegerField()
    currency_id = models.IntegerField()
    description = models.CharField(max_length=100)
    global_nominal_account = models.ForeignKey(
        GlobalNominalAccount,
        models.CASCADE,
        related_name='address_nominal_accounts',
    )

    objects = AddressNominalAccountManager()

    class Meta:
        """
        Metadata about the model for Django to use in whatever way it sees fit
        """
        db_table = 'address_nominal_account'

        indexes = [
            # Indexing everything in the `search_fields` map in List Controller
            models.Index(fields=['id'], name='address_account_id'),
            models.Index(fields=['address_id'], name='address_account_address_id'),
            models.Index(fields=['deleted'], name='address_account_deleted'),
        ]
        ordering = ['-address_id']
