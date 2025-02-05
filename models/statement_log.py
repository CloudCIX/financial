# libs
from cloudcix_rest.models import BaseModel
from django.db import models


__all__ = [
    'StatementLog',
]


class StatementLog(BaseModel):
    """
    The StatementLog model records the data related to when an automated statement tries to be sent to a partner address
    """
    address_id = models.IntegerField()
    comment = models.TextField()
    contra_address_id = models.IntegerField()
    status = models.CharField(max_length=10)

    class Meta:
        """
        Metadata about the model for Django to use in whatever way it sees fit
        """
        db_table = 'statement_log'
