"""
Dummy serializers to generate Creditor Ledger schema
"""
# libs
import serpy

__all__ = [
    'CreditorLedgerSerializer',
    'CreditorLedgerAgedSerializer',
]


class CreditorLedgerSerializer(serpy.Serializer):
    """
    address_id:
        description: The id of the Address for one of the User's Creditors
        type: integer
    balance:
        description: The outstanding balance between the User and one of their Creditors
        type: string
        format: decimal
    """
    address_id = serpy.Field()
    balance = serpy.Field()


class CreditorLedgerAgedSerializer(serpy.Serializer):
    """
    address_id:
        description: The id of the Address for one of the User's Creditors
        type: integer
    balance_30_day:
        description: The outstanding balance between the User and a Creditor from the past 30 days
        type: string
        format: decimal
    balance_60_day:
        description: The outstanding balance between the User and a Creditor from the past 30 to 60 days
        type: string
        format: decimal
    balance_90_day:
        description: The outstanding balance between the User and a Creditor from the past 60 to 90 days
        type: string
        format: decimal
    balance_120_day:
        description: The outstanding balance between the User and a Creditor from the past 90 to 120 days
        type: string
        format: decimal
    current_balance:
        description: The total amount that the requesting User owes, or is owed by, one of their Creditors
        type: string
        format: decimal
    older_balance:
        description: The outstanding balance between the User and a Creditor from over 120 days ago
        type: string
        format: decimal
    """
    address_id = serpy.Field()
    balance_30_day = serpy.Field()
    balance_60_day = serpy.Field()
    balance_90_day = serpy.Field()
    balance_120_day = serpy.Field()
    current_balance = serpy.Field()
    older_balance = serpy.Field()
