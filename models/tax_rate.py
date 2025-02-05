# stdlib
from datetime import datetime
# libs
from cloudcix_rest.models import BaseModel
from django.db import models
from django.urls import reverse


__all__ = [
    'TaxRate',
]


class TaxRate(BaseModel):
    """
    The Tax Rate model represents a percentage that can be applied to a line of an invoice
    """
    address_id = models.IntegerField()
    description = models.CharField(max_length=50)
    percent = models.DecimalField(decimal_places=4, max_digits=23)

    class Meta:
        db_table = 'tax_rate'

        indexes = [
            # Indexing everything in the `search_fields` map in List Controller
            models.Index(fields=['id'], name='tax_rate_id'),
            models.Index(fields=['address_id'], name='tax_rate_address_id'),
            models.Index(fields=['deleted'], name='tax_rate_deleted'),
            models.Index(fields=['description'], name='tax_rate_description'),
            models.Index(fields=['percent'], name='tax_rate_percent'),
        ]
        ordering = ['address_id']

    def get_absolute_url(self) -> str:
        """
        Generates the absolute URL that corresponds to the TaxRateResource view for this Tax Rate record
        :return: A URL that corresponds to the views for this Tax Rate record
        """
        return reverse('tax_rate_resource', kwargs={'pk': self.pk})

    def set_deleted(self):
        """
        Update the Tax Rate model to set its deleted field to now
        """
        self.deleted = datetime.utcnow()
        self.save()
