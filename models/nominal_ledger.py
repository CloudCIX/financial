# stdlib
from datetime import datetime
# libs
from cloudcix_rest.models import BaseManager, BaseModel
from django.db import models
from django.urls import reverse


__all__ = [
    'NominalLedger',
]


class NominalLedgerManager(BaseManager):
    """
    Manager for Nominal Ledger model which filters by the Transaction Type id passed to the constructor, and pre-fetches
    foreign keys to speed up serialization
    """

    def __init__(self, transaction_type_id=None):
        super(NominalLedgerManager, self).__init__()
        self.transaction_type_id = transaction_type_id

    def create(self, *args, **kwargs):
        if 'transaction_type_id' not in kwargs:
            kwargs['transaction_type_id'] = self.transaction_type_id
        return super(NominalLedgerManager, self).create(*args, **kwargs)

    def get_queryset(self) -> models.QuerySet:
        """
        Extend the BaseManager QuerySet to filter by the Manager's Transaction Type id and pre-fetch foreign keys
        :return: A base queryset which can be further extended but only returns entries of the given Transaction Type id
        """
        query = super().get_queryset().prefetch_related(
            'credits',
            'debits',
        ).select_related(
            'contra_nominal_ledger',
        )
        if self.transaction_type_id is not None:
            query = query.filter(transaction_type_id=self.transaction_type_id)
        return query


class NominalLedger(BaseModel):
    """
    The Nominal Ledger model records the transactions for all Nominal Accounts
    The billing address needs to be recorded explicitly so that if a Member changes their details, any transactions with
    them in the Nominal Ledger will be unaffected.
    """
    address_id = models.IntegerField()
    address1_bill_to = models.CharField(max_length=100, null=True)
    address1_deliver_to = models.CharField(max_length=100, null=True)
    address2_bill_to = models.CharField(max_length=100, null=True)
    address2_deliver_to = models.CharField(max_length=100, null=True)
    address3_bill_to = models.CharField(max_length=100, null=True)
    address3_deliver_to = models.CharField(max_length=100, null=True)
    city_bill_to = models.CharField(max_length=50, null=True)
    city_deliver_to = models.CharField(max_length=50, null=True)
    contact = models.CharField(max_length=100, default='No Contact')
    contra_address_id = models.IntegerField(null=True)
    contra_contact = models.CharField(max_length=100, null=True)
    contra_nominal_ledger = models.ForeignKey('self', models.CASCADE, null=True)
    country_id_bill_to = models.IntegerField(null=True)
    country_id_deliver_to = models.IntegerField(null=True)
    external_reference = models.CharField(max_length=50, null=True)
    name_bill_to = models.CharField(max_length=250, null=True)
    name_deliver_to = models.CharField(max_length=250, null=True)
    narrative = models.CharField(max_length=250, null=True)
    period_end_balance = models.DecimalField(decimal_places=4, max_digits=23, null=True)
    postcode_bill_to = models.CharField(max_length=20, null=True)
    postcode_deliver_to = models.CharField(max_length=20, null=True)
    report_template_id = models.IntegerField(null=True)
    subdivision_id_bill_to = models.IntegerField(null=True)
    subdivision_id_deliver_to = models.IntegerField(null=True)
    transaction_date = models.DateField()
    transaction_type_id = models.IntegerField()
    tsn = models.IntegerField()
    unallocated_balance = models.DecimalField(decimal_places=4, max_digits=23, default=0.0000)

    # Managers
    objects = NominalLedgerManager()
    account_purchase_adjustments = NominalLedgerManager(transaction_type_id=10005)
    account_purchase_debit_notes = NominalLedgerManager(transaction_type_id=10003)
    account_purchase_invoices = NominalLedgerManager(transaction_type_id=10002)
    account_purchase_payments = NominalLedgerManager(transaction_type_id=10004)
    account_sale_adjustments = NominalLedgerManager(transaction_type_id=11005)
    account_sale_credit_notes = NominalLedgerManager(transaction_type_id=11003)
    account_sale_invoices = NominalLedgerManager(transaction_type_id=11002)
    account_sale_payments = NominalLedgerManager(transaction_type_id=11004)
    cash_purchase_invoices = NominalLedgerManager(transaction_type_id=10000)
    cash_purchase_debit_notes = NominalLedgerManager(transaction_type_id=10001)
    cash_purchase_receipts = NominalLedgerManager(transaction_type_id=10006)
    cash_purchase_refunds = NominalLedgerManager(transaction_type_id=10007)
    cash_sale_credit_notes = NominalLedgerManager(transaction_type_id=11001)
    cash_sale_invoices = NominalLedgerManager(transaction_type_id=11000)
    cash_sale_receipts = NominalLedgerManager(transaction_type_id=11006)
    cash_sale_refunds = NominalLedgerManager(transaction_type_id=11007)
    journal_entries = NominalLedgerManager(transaction_type_id=12000)
    period_end = NominalLedgerManager(transaction_type_id=12001)
    year_ends = NominalLedgerManager(transaction_type_id=12002)

    class Meta:
        """
        Metadata about the model for Django to use in whatever way it sees fit
        """
        db_table = 'nominal_ledger'

        indexes = [
            # Indexing everything in the `search_fields` map in List Controller
            models.Index(fields=['id'], name='ledger_id'),
            models.Index(fields=['address_id'], name='ledger_address_id'),
            models.Index(fields=['contra_address_id'], name='ledger_contra_address_id'),
            models.Index(fields=['contra_nominal_ledger'], name='ledger_contra_nominal_ledger'),
            models.Index(fields=['deleted'], name='ledger_deleted'),
            models.Index(fields=['narrative'], name='ledger_narrative'),
            models.Index(fields=['period_end_balance'], name='ledger_period_end_balance'),
            models.Index(fields=['transaction_date'], name='ledger_transaction_date'),
            models.Index(fields=['transaction_type_id'], name='ledger_transaction_type_id'),
            models.Index(fields=['tsn'], name='ledger_tsn'),
            models.Index(fields=['unallocated_balance'], name='ledger_unallocated_balance'),
        ]
        ordering = ['transaction_date']

    def get_absolute_url(self) -> str:
        """
        Generates the absolute URL that corresponds to the Resource view for this Nominal Ledger record
        :return: A URL that corresponds to the views for this Nominal Ledger record
        """
        urls = {
            10000: 'cash_purchase_invoice_resource',
            10001: 'cash_purchase_debit_note_resource',
            10002: 'account_purchase_invoice_resource',
            10003: 'account_purchase_debit_note_resource',
            10004: 'account_purchase_payment_resource',
            10005: 'account_purchase_adjustment_resource',
            10006: 'cash_purchase_receipt_resource',
            10007: 'cash_purchase_refund_resource',
            11000: 'cash_sale_invoice_resource',
            11001: 'cash_sale_credit_note_resource',
            11002: 'account_sale_invoice_resource',
            11003: 'account_sale_credit_note_resource',
            11004: 'account_sale_payment_resource',
            11005: 'account_sale_adjustment_resource',
            11006: 'cash_sale_receipt_resource',
            11007: 'cash_sale_refund_resource',
            12000: 'journal_entry_resource',
            12001: 'period_end_resource',
            12002: 'year_end_resource',
        }
        return reverse(urls[self.transaction_type_id], kwargs={'tsn': self.tsn})

    def set_deleted(self):
        """
        Set the deleted field on a Nominal Ledger record and propagate it to the debits and credits
        Not all Transaction Types can be deleted
        """
        if self.transaction_type_id not in (12001, 12002):
            return None
        deltime = datetime.utcnow()
        self.deleted = deltime
        self.save()
        self.credits.all().update(deleted=deltime)
        self.debits.all().update(deleted=deltime)

    def save(self, *args, **kwargs):
        """
        After an object is create/updated, refresh it from the database to get the Transaction Sequence Number
        """
        super(NominalLedger, self).save(*args, **kwargs)
        self.refresh_from_db()
