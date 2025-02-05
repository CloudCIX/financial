# stdlib
from decimal import Decimal
# libs
from django.db.models import Q, Sum
import serpy
# local
from financial import reserved_accounts as reserved
from financial.models import NominalLedgerCredit, NominalLedgerDebit
from financial.serializers.custom_fields import DecimalField
from financial.serializers.nominal_ledger import NominalLedgerSerializer


__all__ = [
    'CreditorAccountHistorySerializer',
    'CreditorAccountStatementSerializer',
]


class CreditorAccountHistorySerializer(NominalLedgerSerializer):
    """
    address_id:
        description: The id of the Address that created the Nominal Ledger entry
        type: integer
    address1_bill_to:
        description: The first line of the address to bill for the transaction
        type: string
    address1_deliver_to:
        description: The first line of the address to deliver the transaction SKU items to
        type: string
    address2_bill_to:
        description: The second line of the address to bill for the transaction
        type: string
    address2_deliver_to:
        description: The second line of the address to deliver the transaction SKU items to
        type: string
    address3_bill_to:
        description: The third line of the address to bill for the transaction
        type: string
    address3_deliver_to:
        description: The third line of the address to deliver the transaction SKU items to
        type: string
    city_bill_to:
        description: The city in which the company to bill for the transaction line is located
        type: string
    city_deliver_to:
        description: The city in which the company to deliver the SKU items is located
        type: string
    contact:
        description: The name of the User who created the Nominal Ledger entry
        type: string
    contra_address_id:
        description: |
            The Address id of another Financial User who created a transaction between their own Address and the current
            User's Address
        type: integer
    contra_contact:
        description: |
            The name of another User of the Financial application that created a transaction with the current User's
            Address
        type: string
    contra_nominal_ledger_id:
        description: The id of the Nominal Ledger entry that was created in response to the current Transaction
        type: integer
    country_id_bill_to:
        description: The id of the Country in which the company to bill for the transaction is located
        type: integer
    country_id_deliver_to:
        description: The id of the Country in which the company to deliver the SKU items is located
        type: integer
    created:
        description: The date that the Nominal Ledger entry was created
        type: string
    credits:
        $ref: '#/components/schemas/NominalLedgerLine'
    debits:
        $ref: '#/components/schemas/NominalLedgerLine'
    email_log:
        $ref: '#/components/schemas/EmailLog'
    external_reference:
        description: The referencing system that the User's Member uses to track transactions
        type: string
    id:
        description: The id of the Nominal Ledger record
        type: integer
    name_bill_to:
        description: The name of the company that the transaction will be billed to
        type: string
    name_deliver_to:
        description: The name of the company that the transaction's SKU items will be delivered to
        type: integer
    narrative:
        description: A description of the transaction that created the Nominal Ledger entry
        type: string
    report_template_id:
        description: The id of the Report Template to use when printing this Nominal Ledger entry
        type: integer
    running_balance:
        description: The total amount owed to the Creditor for all Purchase transactions up to this one
        type: string
        format: decimal
    postcode_bill_to:
        description: The postcode of the company that the transaction will be billed to
        type: string
    postcode_deliver_to:
        description: The postcode of the company that the transaction's SKU items will be delivered to
        type: string
    subdivision_id_bill_to:
        description: The id of the Subdivision in which the company to bill for the transaction is located
        type: integer
    subdivision_id_deliver_to:
        description: The id of the Subdivision in which the company to deliver the SKU items is located
        type: integer
    transaction_date:
        description: The date that the transaction took place
        type: string
    transaction_type_id:
        description: The id of the Transaction Type that the Nominal Ledger entry uses
        type: integer
    tsn:
        description: |
            The Transaction Sequence Number. Each Transaction Type in an Address has its own Transaction Sequence
            Numbers that begins at one and increments each time a transaction of that type is created.
        type: integer
    unallocated_balance:
        description: The amount left unpaid on a transaction
        type: string
        format: decimal
    updated:
        description: The date that the Nominal Ledger entry was last updated
        type: string
    uri:
        description: |
            The absolute URL of the Nominal Ledger entry that can be used to perform `Read` and `Update` operations
        type: string
    """
    running_balance = serpy.MethodField()

    def get_running_balance(self, obj):
        """
        Calculate the total amount owed up to and including the current transaction
        :param obj: The transaction being serialized
        :return: The total debits minus credits from all transactions before this one
        """
        # Get all the transactions before the current transaction
        date_query = Q(nominal_ledger__transaction_date__lt=obj.transaction_date) | \
            Q(nominal_ledger__transaction_date=obj.transaction_date) & Q(nominal_ledger_id__lte=obj.id)

        # Get the purchase adjustments where the Creditor Control Account is debited/credited
        creditor_adjustment = Q(nominal_ledger__transaction_type_id=10005) & \
            Q(nominal_account_number=reserved.CREDITOR_CONTROL_ACCOUNT)

        debits = Decimal(str(NominalLedgerDebit.objects.filter(
            date_query,
            creditor_adjustment | Q(nominal_ledger__transaction_type_id__in=[10003, 10004]),
            nominal_ledger__address_id=obj.address_id,
            nominal_ledger__contra_address_id=obj.contra_address_id,
        ).aggregate(
            Sum('amount'),
        )['amount__sum'] or 0))

        credits = Decimal(str(NominalLedgerCredit.objects.filter(
            date_query,
            creditor_adjustment | Q(nominal_ledger__transaction_type_id=10002),
            nominal_ledger__address_id=obj.address_id,
            nominal_ledger__contra_address_id=obj.contra_address_id,
        ).aggregate(
            Sum('amount'),
        )['amount__sum'] or 0))

        return str((debits - credits).quantize(Decimal('1.0000')))


class CreditorAccountStatementSerializer(NominalLedgerSerializer):
    """
    address_id:
        description: The id of the Address that created the Nominal Ledger entry
        type: integer
    address1_bill_to:
        description: The first line of the address to bill for the transaction
        type: string
    address1_deliver_to:
        description: The first line of the address to deliver the transaction SKU items to
        type: string
    address2_bill_to:
        description: The second line of the address to bill for the transaction
        type: string
    address2_deliver_to:
        description: The second line of the address to deliver the transaction SKU items to
        type: string
    address3_bill_to:
        description: The third line of the address to bill for the transaction
        type: string
    address3_deliver_to:
        description: The third line of the address to deliver the transaction SKU items to
        type: string
    city_bill_to:
        description: The city in which the company to bill for the transaction line is located
        type: string
    city_deliver_to:
        description: The city in which the company to deliver the SKU items is located
        type: string
    contact:
        description: The name of the User who created the Nominal Ledger entry
        type: string
    contra_address_id:
        description: |
            The Address id of another Financial User who created a transaction between their own Address and the current
            User's Address
        type: integer
    contra_contact:
        description: |
            The name of another User of the Financial application that created a transaction with the current User's
            Address
        type: string
    contra_nominal_ledger_id:
        description: The id of the Nominal Ledger entry that was created in response to the current Transaction
        type: integer
    country_id_bill_to:
        description: The id of the Country in which the company to bill for the transaction is located
        type: integer
    country_id_deliver_to:
        description: The id of the Country in which the company to deliver the SKU items is located
        type: integer
    created:
        description: The date that the Nominal Ledger entry was created
        type: string
    credits:
        $ref: '#/components/schemas/NominalLedgerLine'
    debits:
        $ref: '#/components/schemas/NominalLedgerLine'
    email_log:
        $ref: '#/components/schemas/EmailLog'
    external_reference:
        description: The referencing system that the User's Member uses to track transactions
        type: string
    id:
        description: The id of the Nominal Ledger record
        type: integer
    name_bill_to:
        description: The name of the company that the transaction will be billed to
        type: string
    name_deliver_to:
        description: The name of the company that the transaction's SKU items will be delivered to
        type: integer
    narrative:
        description: A description of the transaction that created the Nominal Ledger entry
        type: string
    report_template_id:
        description: The id of the Report Template to use when printing this Nominal Ledger entry
        type: integer
    running_balance:
        description: The outstanding amount owed to the Creditor for all Purchase transactions up to this one
        type: string
        format: decimal
    postcode_bill_to:
        description: The postcode of the company that the transaction will be billed to
        type: string
    postcode_deliver_to:
        description: The postcode of the company that the transaction's SKU items will be delivered to
        type: string
    subdivision_id_bill_to:
        description: The id of the Subdivision in which the company to bill for the transaction is located
        type: integer
    subdivision_id_deliver_to:
        description: The id of the Subdivision in which the company to deliver the SKU items is located
        type: integer
    transaction_date:
        description: The date that the transaction took place
        type: string
    transaction_type_id:
        description: The id of the Transaction Type that the Nominal Ledger entry uses
        type: integer
    tsn:
        description: |
            The Transaction Sequence Number. Each Transaction Type in an Address has its own Transaction Sequence
            Numbers that begins at one and increments each time a transaction of that type is created.
        type: integer
    unallocated_balance:
        description: The amount left unpaid on a transaction
        type: string
        format: decimal
    updated:
        description: The date that the Nominal Ledger entry was last updated
        type: string
    uri:
        description: |
            The absolute URL of the Nominal Ledger entry that can be used to perform `Read` and `Update` operations
        type: string
    """
    running_balance = DecimalField()
