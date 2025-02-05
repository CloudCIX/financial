# libs
import serpy
# local
from financial.models.nominal_ledger import NominalLedger
from financial.serializers.email_log import EmailLogSerializer


__all__ = [
    'PeriodEndSerializer',
]


class PeriodEndSerializer(serpy.Serializer):
    """
    address_id:
        description: The id of the Address that created the Period End
        type: integer
    contact:
        description: The name of the User who created the Period End
        type: string
    created:
        description: Timestamp, in ISO format, of when the Period End record was created.
        type: string
    email_log:
        $ref: '#/components/schemas/EmailLog'
    narrative:
        description: A description of the Period End
        type: string
    period_end_balance:
        description: |
            The total balance of debits/credits that occurred between the previous Period End and the current Period End
        type: string
        format: decimal
    transaction_date:
        description: A date that defines the end of the Financial Period
        type: string
    tsn:
        description: |
            The Transaction Sequence Number. Each Transaction Type in an Address has its own Transaction Sequence
            Numbers that begins at one and increments each time a transaction of that type is created.
        type: integer
    uri:
        description: |
            The absolute URL of the Nominal Ledger entry that can be used to perform `Read` and `Delete` operations
        type: string
    year_end:
        description: A flag stating whether this Period End transaction coincides with a Year End transaction
        type: bool
    """
    address_id = serpy.Field()
    contact = serpy.Field()
    created = serpy.Field(attr='created.isoformat', call=True)
    email_log = EmailLogSerializer(many=True, attr='email_log.all', call=True)
    narrative = serpy.Field()
    period_end_balance = serpy.StrField()
    transaction_date = serpy.Field(attr='transaction_date.isoformat', call=True)
    tsn = serpy.Field()
    uri = serpy.Field(attr='get_absolute_url', call=True)
    year_end = serpy.MethodField()

    def get_year_end(self, obj):
        return NominalLedger.year_ends.filter(
            address_id=obj.address_id,
            transaction_date=obj.transaction_date,
        ).exists()
