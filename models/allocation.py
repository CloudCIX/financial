# stdlib
from datetime import datetime
# libs
from cloudcix_rest.models import BaseManager, BaseModel
from django.db import models
from django.urls import reverse


__all__ = [
    'Allocation',
]


class AllocationManager(BaseManager):
    """
    Manager for Allocation which pre-fetches foreign keys
    """

    def get_queryset(self) -> models.QuerySet:
        """
        Extend the BaseManager QuerySet to prefetch all related data in every query to speed up serialization
        :return: A base queryset which can be further extended but always pre-fetches necessary data
        """
        return super().get_queryset().prefetch_related(
            'details',
            'details__nominal_ledger',
        )


class Allocation(BaseModel):
    """
    An Allocation record represents a transaction matched against another to balance their Debits and Credits and mark
    them as processed
    """
    address_id = models.IntegerField()
    nominal_account_number = models.IntegerField()

    objects = AllocationManager()

    class Meta:
        """
        Metadata about the model for Django to use in whatever way it sees fit
        """
        db_table = 'allocation'

        indexes = [
            # Indexing everything in the `search_fields` map in List Controller
            models.Index(fields=['created'], name='allocation_created'),
            models.Index(fields=['deleted'], name='allocation_deleted'),
            models.Index(fields=['id'], name='allocation_id'),
        ]

    def get_absolute_url(self) -> str:
        """
        Generates the absolute URL that corresponds to the AllocationResource view for this VM record
        :return: A URL that corresponds to the views for this VM record
        """
        return reverse('allocation_resource', kwargs={'pk': self.pk})

    def set_deleted(self):
        """
        Update the Allocation model to set its deleted field to now, and propagate to all of the children of the
        Allocation
        """
        deltime = datetime.utcnow()
        self.deleted = deltime
        self.save()
        # Loop through all the Allocation Details belonging to the Allocation and delete them
        for detail in self.details.iterator():
            detail.deleted = deltime
            detail.save()
