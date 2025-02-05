# stdlib
from datetime import datetime
# libs
from cloudcix_rest.models import BaseManager, BaseModel
from django.db import models
from django.urls import reverse
# local
from .global_nominal_account import GlobalNominalAccount
from .payment_method import PaymentMethod


__all__ = [
    'NominalContra',
]


class NominalContraManager(BaseManager):
    """
    Manager for Nominal Contra which pre-fetches foreign keys
    """

    def get_queryset(self) -> models.QuerySet:
        """
        Extend the BaseManager QuerySet to prefetch all related data in every query to speed up serialization
        :return: A base queryset which can be further extended but always pre-fetches necessary data
        """
        return super().get_queryset().select_related(
            'global_nominal_account',
            'global_nominal_account__nominal_account_type',
            'payment_method',
        )


class NominalContra(BaseModel):
    """
    The Nominal Contra model represents an association between a Transaction, a Payment Method, and a Nominal Account.
    When a Transaction is processed, the Transaction Type and Payment Method determine which Nominal Account will be
    used to balance the Transaction
    """
    global_nominal_account = models.ForeignKey(GlobalNominalAccount, models.CASCADE)
    payment_method = models.ForeignKey(PaymentMethod, models.CASCADE)
    transaction_type_id = models.IntegerField()

    objects = NominalContraManager()

    class Meta:
        """
        Metadata about the model for Django to use in whatever way it sees fit
        """
        db_table = 'nominal_contra'

        indexes = [
            # Indexing everything in the `search_fields` map in List Controller
            models.Index(fields=['id'], name='nom_contra_id'),
            models.Index(fields=['deleted'], name='nom_contra_deleted'),
            models.Index(fields=['transaction_type_id'], name='nom_contra_transaction_type_id'),
        ]
        ordering = ['global_nominal_account_id']

    def get_absolute_url(self) -> str:
        """
        Generates the absolute URL that corresponds to the NominalContraResource view for this Nominal Contra record
        :return: A URL that corresponds to the views for this Nominal Contra record
        """
        return reverse('nominal_contra_resource', kwargs={'pk': self.pk})

    def set_deleted(self):
        """
        Update the Nominal Contra model to set its deleted field to now
        """
        self.deleted = datetime.utcnow()
        self.save()
