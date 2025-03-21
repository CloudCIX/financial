# libs
from cloudcix_rest.models import BaseManager, BaseModel
from django.db import models
# local
from .nominal_ledger import NominalLedger
from .tax_rate import TaxRate


__all__ = [
    'NominalLedgerDebit',
]


class NominalLedgerDebitManager(BaseManager):
    """
    Manager for Nominal Ledger Credit which pre-fetches foreign keys
    """

    def get_queryset(self) -> models.QuerySet:
        """
        Extend the BaseManager QuerySet to prefetch all related data in every query
        :return: A base queryset which can be further extended but always pre-fetches necessary data
        """
        return super().get_queryset().select_related(
            'nominal_ledger',
        )


class NominalLedgerDebit(BaseModel):
    """
    The Nominal Ledger Debit model represents the amount that is debited from each Nominal Account in a transaction
    """
    amount = models.DecimalField(decimal_places=4, max_digits=23)
    description = models.CharField(max_length=250, null=True)
    exchange_rate = models.DecimalField(decimal_places=4, max_digits=23, default='1.0000')
    nominal_account_number = models.IntegerField()
    nominal_ledger = models.ForeignKey(NominalLedger, models.CASCADE, related_name='debits')
    part_number = models.CharField(max_length=250, null=True)
    quantity = models.DecimalField(decimal_places=4, max_digits=18, null=True)
    tax_percent = models.DecimalField(decimal_places=4, max_digits=23, null=True)
    tax_rate = models.ForeignKey(TaxRate, models.CASCADE, null=True)
    unit_price = models.DecimalField(decimal_places=8, max_digits=23, null=True)

    objects = NominalLedgerDebitManager()

    class Meta:
        """
        Metadata about the model for Django to use in whatever way it sees fit
        """
        db_table = 'nominal_ledger_debits'

        indexes = [
            # Indexing everything in the `search_fields` map in List Controller
            models.Index(fields=['id'], name='ledger_debit_id'),
            models.Index(fields=['deleted'], name='ledger_debit_deleted'),
            models.Index(fields=['tax_percent'], name='ledger_debit_tax_percent'),
        ]
