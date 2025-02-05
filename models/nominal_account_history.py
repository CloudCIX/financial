# libs
from django.db import models


class NominalAccountHistory(models.Model):
    """
    A convenience Model for interacting with an sql view in the migrations. Does not create a table of its own,
    signified by Meta.managed = False.
    Used for filtering transactions on the Nominal Ledger by the Nominal Account that is debited/credited
    """
    address_id = models.IntegerField()
    amount = models.DecimalField(decimal_places=4, max_digits=23)
    contra_address_id = models.IntegerField()
    id = models.IntegerField(primary_key=True)
    nominal_ledger = models.ForeignKey('NominalLedger', on_delete=models.DO_NOTHING)
    name_bill_to = models.CharField(max_length=250, null=True)
    narrative = models.CharField(max_length=250, null=True)
    nominal_account_number = models.IntegerField()
    transaction_type_id = models.IntegerField()
    transaction_date = models.DateTimeField()
    tsn = models.IntegerField()

    class Meta:
        db_table = 'nominal_account_history'
        managed = False
