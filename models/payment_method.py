# stdlib
from datetime import datetime
# libs
from cloudcix_rest.models import BaseModel
from django.db import models
from django.urls import reverse


__all__ = [
    'PaymentMethod',
]


class PaymentMethod(BaseModel):
    """
    The Payment Method model represents the different ways to pay for a transaction
    """
    description = models.CharField(max_length=20)
    member_id = models.IntegerField()

    class Meta:
        """
        Metadata about the model for Django to use in whatever way it sees fit
        """
        db_table = 'payment_method'

        indexes = [
            # Indexing everything in the `search_fields` map in List Controller
            models.Index(fields=['id'], name='payment_method_id'),
            models.Index(fields=['deleted'], name='payment_method_deleted'),
            models.Index(fields=['description'], name='payment_method_description'),
        ]
        ordering = ['description']

    def get_absolute_url(self) -> str:
        """
        Generates the absolute URL that corresponds to the PaymentMethodResource view for this PaymentMethod record
        :return: A URL that corresponds to the views for this PaymentMethod record
        """
        return reverse('payment_method_resource', kwargs={'pk': self.pk})

    def set_deleted(self):
        """
        Update the Payment Method model to set its deleted field to now, and propagate to all of the children of the
        PaymentMethod
        """
        deltime = datetime.utcnow()
        self.deleted = deltime
        self.save()
        # Loop through all the Nominal Contras belonging to the Payment Method and delete them
        for contra in self.nominalcontra_set.all().iterator():
            contra.deleted = deltime
            contra.save()
