# libs
from cloudcix_rest.models import BaseModel
from django.db import models
# local
from .nominal_ledger import NominalLedger

__all__ = [
    'EmailLog',
]


class EmailLog(BaseModel):
    """
    The EmailLog model records the data related to when an email is sent when a transaction is created
    """
    comment = models.TextField()
    email_from = models.CharField(max_length=255)
    email_to = models.CharField(max_length=255)
    nominal_ledger = models.ForeignKey(NominalLedger, models.CASCADE, related_name='email_log')
    receiver_user_id = models.IntegerField()
    sender_user_id = models.IntegerField()
    status = models.CharField(max_length=10)

    class Meta:
        """
        Metadata about the model for Django to use in whatever way it sees fit
        """
        db_table = 'email_log'
