# libs
from cloudcix_rest.models import BaseManager, BaseModel
from django.db import models
# local
from .allocation import Allocation
from .nominal_ledger import NominalLedger


__all__ = [
    'AllocationDetail',
]


class AllocationDetailManager(BaseManager):
    """
    Manager for Allocation Detail which pre-fetches foreign keys
    """

    def get_queryset(self) -> models.QuerySet:
        """
        Extend the BaseManager QuerySet to prefetch all related data in every query to speed up serialization
        :return: A base queryset which can be further extended but always pre-fetches necessary data
        """
        return super().get_queryset().select_related(
            'nominal_ledger',
        )


class AllocationDetail(BaseModel):
    """
    The Allocation Detail model represents the amount debited or credited from an account to balance a Nominal Ledger
    """
    allocation = models.ForeignKey(Allocation, related_name='details', on_delete=models.CASCADE)
    credit_amount = models.DecimalField(decimal_places=4, max_digits=23)
    debit_amount = models.DecimalField(decimal_places=4, max_digits=23)
    nominal_ledger = models.ForeignKey(NominalLedger, models.CASCADE)

    objects = AllocationDetailManager()

    class Meta:
        """
        Metadata about the model for Django to use in whatever way it sees fit
        """
        db_table = 'allocation_detail'
