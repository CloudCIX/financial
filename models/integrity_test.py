# libs
from django.db import models


__all__ = [
    'IntegrityTest',
]


class IntegrityTest(models.Model):
    """
    The Integrity Test model represents the data stored in relation to the Integrity Test. Examples
    include 'Fixed Assets', 'Current Liabilities', etc.
    """
    start_time = models.DateTimeField()
    finish_time = models.DateTimeField()
    records_tested = models.IntegerField()
    errors_found = models.IntegerField()

    class Meta:
        """
        Metadata about the model for Django to use in whatever way it sees fit
        """
        db_table = 'integrity_test'
