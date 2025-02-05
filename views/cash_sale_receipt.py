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
from financial.controllers import CashSaleReceiptCreateController, CashSaleReceiptUpdateController
from financial.models import NominalLedger, NominalLedgerCredit, NominalLedgerDebit
from financial.permissions.cash_sale_receipt import Permissions
from financial.views.transaction_base import Collection, Resource


class CashSaleReceiptCollection(Collection):
    """
    Handles methods regarding Cash Sale Receipts that don't require an id to be specified i.e. create
    """

    def __init__(self, *args, **kwargs):
        super(CashSaleReceiptCollection, self).__init__(
            CashSaleReceiptCreateController,
            11006,
            Permissions,
            *args,
            **kwargs,
        )

    def post(self, request: Request) -> Response:
        """
        summary: Create a Nominal Ledger record where the Transaction Type is for Cash Sale Receipts

        description: |
            Create a new Nominal Ledger record using data supplied by the User and set the Transaction Type to be for
            Cash Sale Receipts

        responses:
            200:
                description: Nominal Ledger record was created successfully
            400: {}
            403: {}
        """
        return self._post(request)

    def _pop_cleaned_data(self, controller: CashSaleReceiptCreateController):
        return {
            'debit': controller.cleaned_data.pop('debit'),
            'credits': controller.cleaned_data.pop('credits'),
            'address_account': controller.cleaned_data.pop('address_account'),
        }

    def _pre_save_operations(self, request: Request, ledger_obj: NominalLedger, popped_data: Dict):
        ledger_obj.country_id_bill_to = request.user.address['country_id']

    def _save_credits(self, ledger_obj: NominalLedger, popped_data: dict):
        lines: Deque = deque()
        for credit in popped_data['credits']:
            lines.append(NominalLedgerCredit(
                nominal_ledger=ledger_obj,
                **credit,
            ))
        NominalLedgerCredit.objects.bulk_create(lines)

    def _save_debits(self, ledger_obj: NominalLedger, popped_data: Dict):
        NominalLedgerDebit.objects.create(
            description=popped_data['address_account'].description,
            nominal_account_number=popped_data['address_account'].global_nominal_account.nominal_account_number,
            nominal_ledger=ledger_obj,
            **popped_data['debit'],
        )


class CashSaleReceiptResource(Resource):
    """
    Handles methods regarding Cash Sale Receipts that don't require an id to be specified i.e. create
    """
    def __init__(self, *args, **kwargs):
        super(CashSaleReceiptResource, self).__init__(
            11006,
            Permissions,
            ('financial_cash_sale_receipt_read_001',),
            ('financial_cash_sale_receipt_update_001', CashSaleReceiptUpdateController),
            *args,
            **kwargs,
        )

    def get(self, request: Request, tsn: int) -> Response:
        """
        summary: Read the details of a specific Cash Sale Receipt record

        description: |
            Attempt to read a Nominal Ledger entry by the given tsn where the Transaction Type is for Cash Sale
            Receipts, returning a 404 if it does not exist

        path_params:
            tsn:
                description: The Transaction Sequence Number of the Cash Sale Receipt to read
                type: integer

        responses:
            200:
                description: The Cash Sale Receipt record was read successfully
            400: {}
            403: {}
            404: {}
        """
        return self._get(request, tsn)

    def put(self, request: Request, tsn: int, partial: bool = False) -> Response:
        """
        summary: Update the details of an existing Cash Sale Resource

        description: |
            Attempt to update the details of an existing Nominal Ledger entry where the Transaction Type is for Cash
            Sale Receipts, returning a 404 if it doesn't exist

        path_params:
            tsn:
                description: The Transaction Sequence Number of the Cash Sale Receipt record to be updated
                type: integer

        responses:
            200:
                description: The Cash Sale Receipt record was updated successfully
            400: {}
            403: {}
            404: {}
        """
        return self._put(request, tsn, partial)
