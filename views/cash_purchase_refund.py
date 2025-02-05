"""
Management for Cash Purchase Refund transactions
"""

# stdlib
from collections import deque
from typing import Deque, Dict
# libs
from rest_framework.request import Request
from rest_framework.response import Response
# local
from financial.controllers.cash_purchase_refund import (
    CashPurchaseRefundCreateController,
    CashPurchaseRefundUpdateController,
)
from financial.models import NominalLedger, NominalLedgerCredit, NominalLedgerDebit
from financial.permissions.cash_purchase_refund import Permissions
from financial.views.transaction_base import Collection, Resource


__all__ = [
    'CashPurchaseRefundCollection',
    'CashPurchaseRefundResource',
]


class CashPurchaseRefundCollection(Collection):
    """
    Handles methods regarding Cash Purchase Refunds that don't require an id to be specified i.e. create
    """

    def __init__(self, *args, **kwargs):
        super(CashPurchaseRefundCollection, self).__init__(
            CashPurchaseRefundCreateController,
            10007,
            permissions=Permissions,
        )

    def post(self, request: Request) -> Response:
        """
        summary: Create a Nominal Ledger record where the Transaction Type is for Cash Purchase Refunds

        description: |
            Create a new Nominal Ledger record using data supplied by the User and set the Transaction Type to be
            Cash Purchase Refunds

        responses:
            200:
                description: Nominal Ledger entry was created successfully
            400: {}
            403: {}
        """
        return self._post(request)

    def _pop_cleaned_data(self, controller):
        return {
            'debit': controller.cleaned_data.pop('debit'),
            'credits': controller.cleaned_data.pop('credits'),
            'address_account': controller.cleaned_data.pop('address_account'),
        }

    def _pre_save_operations(self, request: Request, ledger_obj: NominalLedger, popped_data: Dict):
        """
        Set the billing country to the country of the requesting User
        """
        ledger_obj.country_id_bill_to = request.user.address['country_id']

    def _save_debits(self, ledger_obj: NominalLedger, popped_data: Dict):
        NominalLedgerDebit.objects.create(
            description=popped_data['address_account'],
            nominal_account_number=popped_data['address_account'].global_nominal_account.nominal_account_number,
            nominal_ledger=ledger_obj,
            **popped_data['debit'],
        )

    def _save_credits(self, ledger_obj: NominalLedger, popped_data: Dict):
        lines: Deque = deque()
        for credit in popped_data['credits']:
            lines.append(NominalLedgerCredit(
                nominal_ledger=ledger_obj,
                **credit,
            ))
        NominalLedgerCredit.objects.bulk_create(lines)


class CashPurchaseRefundResource(Resource):
    """
    Handles methods regarding Cash Purchase Refund that do require an id to be specified i.e. read
    """

    def __init__(self, *args, **kwargs):
        super(CashPurchaseRefundResource, self).__init__(
            10007,
            Permissions,
            read_params=('financial_cash_purchase_refund_read_001',),
            update_params=('financial_cash_purchase_refund_update_001', CashPurchaseRefundUpdateController),
            *args,
            **kwargs,
        )

    def get(self, request: Request, tsn: int) -> Response:
        """
        summary: Read the details of a specific Cash Purchase Refund record

        description: |
            Attempt to read a Nominal Ledger entry where the Transaction Type is for Cash Purchase Refunds, returning
            a 404 if it does not exist

        path_params:
            tsn:
                description: The Transaction Sequence Number of the Cash Purchase Refund record to be retrieved
                type: integer

        responses:
            200:
                description: The Cash Purchase Refund record was read successfully
            404: {}
        """
        return self._get(request, tsn)

    def put(self, request: Request, tsn: int, partial: bool = False) -> Response:
        """
        summary: Update the details of an existing Cash Purchase Refund

        description: |
            Attempt to update the details of an existing Nominal Ledger entry where the Transaction Type is for Cash
            Purchase Refunds, returning a 404 if it doesn't exist

        path_params:
            tsn:
                description: The Transaction Sequence Number of the Cash Purchase Refund record to be updated
                type: integer

        responses:
            200:
                description: The Cash Purchase Refund record was updated successfully
            400: {}
            403: {}
            404: {}
        """
        return self._put(request, tsn, partial)
