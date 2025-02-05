"""
Management for Cash Purchase Receipts
"""

# stdlib
from collections import deque
from typing import Deque, Dict
# libs
from rest_framework.request import Request
from rest_framework.response import Response
# local
from financial.controllers import CashPurchaseReceiptCreateController, CashPurchaseReceiptUpdateController
from financial.models import NominalLedger, NominalLedgerCredit, NominalLedgerDebit
from financial.permissions.cash_purchase_receipt import Permissions
from financial.views.transaction_base import Collection, Resource


class CashPurchaseReceiptCollection(Collection):
    """
    Handles methods regarding Cash Purchase Receipts that don't require an id to be specified i.e. create
    """

    def __init__(self, *args, **kwargs):
        super(CashPurchaseReceiptCollection, self).__init__(
            CashPurchaseReceiptCreateController,
            10006,
            Permissions,
            *args,
            **kwargs,
        )

    def post(self, request: Request) -> Response:
        """
        summary: Create a Nominal Ledger record where the Transaction Type is for Cash Purchase Receipts

        description: |
            Create a new Nominal Ledger record using data supplied by the User and set the Transaction Type to be for
            Cash Purchase Receipts

        responses:
            200:
                description: Nominal Ledger record was created successfully
            400: {}
            403: {}
        """
        return self._post(request)

    def _pop_cleaned_data(self, controller: CashPurchaseReceiptCreateController):
        return {
            'debits': controller.cleaned_data.pop('debits'),
            'credit': controller.cleaned_data.pop('credit'),
            'address_account': controller.cleaned_data.pop('address_account'),
        }

    def _pre_save_operations(self, request: Request, ledger_obj: NominalLedger, popped_data: Dict):
        ledger_obj.country_id_bill_to = request.user.address['country_id']

    def _save_debits(self, ledger_obj, popped_data):
        lines: Deque = deque()
        for debit in popped_data['debits']:
            lines.append(NominalLedgerDebit(
                nominal_ledger=ledger_obj,
                **debit,
            ))
        NominalLedgerDebit.objects.bulk_create(lines)

    def _save_credits(self, ledger_obj, popped_data):
        NominalLedgerCredit.objects.create(
            description=popped_data['address_account'].description,
            nominal_account_number=popped_data['address_account'].global_nominal_account.nominal_account_number,
            nominal_ledger=ledger_obj,
            **popped_data['credit'],
        )


class CashPurchaseReceiptResource(Resource):
    """
    Handles methods regarding Cash Purchase Receipts that do require an id to be specified i.e. read
    """

    def __init__(self, *args, **kwargs):
        super(CashPurchaseReceiptResource, self).__init__(
            10006,
            Permissions,
            read_params=('financial_cash_purchase_receipt_read_001',),
            update_params=('financial_cash_purchase_receipt_update_001', CashPurchaseReceiptUpdateController),
            *args,
            **kwargs,
        )

    def get(self, request: Request, tsn: int) -> Response:
        """
        summary: Read the details of a specific Cash Purchase Receipt record

        description: |
            Attempt to read a Nominal Ledger entry where the Transaction Type is for Cash Purchase Receipts, returning
            a 404 if it does not exist

        path_params:
            tsn:
                description: The Transaction Sequence Number of the Cash Purchase Receipt record to be retrieved
                type: integer

        responses:
            200:
                description: The Cash Purchase Receipt record was read successfully
            404: {}
        """
        return self._get(request, tsn)

    def put(self, request: Request, tsn: int, partial: bool = False) -> Response:
        """
        summary: Update the details of an existing Cash Purchase Receipt

        description: |
            Attempt to update the details of an existing Nominal Ledger entry where the Transaction Type is for Cash
            Purchase Receipts, returning a 404 if it doesn't exist

        path_params:
            tsn:
                description: The Transaction Sequence Number of the Cash Purchase Receipt record to be updated
                type: integer

        responses:
            200:
                description: The Cash Purchase Receipt record was updated successfully
            400: {}
            403: {}
            404: {}
        """
        return self._put(request, tsn, partial)
