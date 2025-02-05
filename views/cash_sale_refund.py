"""
Management for Cash Sale Refunds
"""

# stdlib
from collections import deque
from typing import Deque, Dict
# libs
from rest_framework.request import Request
from rest_framework.response import Response
# local
from financial.controllers.cash_sale_refund import CashSaleRefundCreateController, CashSaleRefundUpdateController
from financial.models import NominalLedger, NominalLedgerCredit, NominalLedgerDebit
from financial.permissions.cash_sale_refund import Permissions
from financial.views.transaction_base import Collection, Resource


__all__ = [
    'CashSaleRefundCollection',
]


class CashSaleRefundCollection(Collection):
    """
    Handles methods regarding Cash Sale Refunds that don't require an id to be specified, i.e. create
    """

    def __init__(self, *args, **kwargs):
        super(CashSaleRefundCollection, self).__init__(
            CashSaleRefundCreateController,
            11007,
            Permissions,
            *args,
            **kwargs,
        )

    def post(self, request: Request) -> Response:
        """
        summary: Create a Nominal Ledger record where the Transaction Type is for Cash Sale Refunds

        description: |
            Create a new Nominal Ledger record using data supplied by the User and set the Transaction Type to be for
            Cash Sale Refunds

        responses:
            200:
                description: Nominal Ledger record was created successfully
            400: {}
            403: {}
        """
        return self._post(request)

    def _pop_cleaned_data(self, controller: CashSaleRefundCreateController):
        return {
            'debits': controller.cleaned_data.pop('debits'),
            'credit': controller.cleaned_data.pop('credit'),
            'address_account': controller.cleaned_data.pop('address_account'),
        }

    def _pre_save_operations(self, request: Request, ledger_obj: NominalLedger, popped_data: Dict):
        """
        Set the country id to the requesting User's country
        """
        ledger_obj.country_id_bill_to = request.user.address['country_id']

    def _save_debits(self, ledger_obj: NominalLedger, popped_data: Dict):
        lines: Deque = deque()
        for debit in popped_data['debits']:
            lines.append(NominalLedgerDebit(
                nominal_ledger=ledger_obj,
                **debit,
            ))
        NominalLedgerDebit.objects.bulk_create(lines)

    def _save_credits(self, ledger_obj: NominalLedger, popped_data: Dict):
        NominalLedgerCredit.objects.create(
            description=popped_data['address_account'].description,
            nominal_account_number=popped_data['address_account'].global_nominal_account.nominal_account_number,
            nominal_ledger=ledger_obj,
            **popped_data['credit'],
        )


class CashSaleRefundResource(Resource):
    """
    Handles methods regarding Cash Sale Refund that do require an id to be specified, i.e. read, update
    """

    def __init__(self, *args, **kwargs):
        super(CashSaleRefundResource, self).__init__(
            11007,
            Permissions,
            ('financial_cash_sale_refund_read_001',),
            ('financial_cash_sale_refund_update_001', CashSaleRefundUpdateController),
            *args,
            **kwargs,
        )

    def get(self, request: Request, tsn: int) -> Response:
        """
        summary: Read the details of a specific Cash Sale Refund record

        description: |
            Attempt to read a Nominal Ledger entry by the given tsn where the Transaction Type is for Cash Sale
            Refunds, returning a 404 if it does not exist

        path_params:
            tsn:
                description: The Transaction Sequence Number of the Cash Sale Refund to read
                type: integer

        responses:
            200:
                description: The Cash Sale Refund record was read successfully
            400: {}
            403: {}
            404: {}
        """
        return self._get(request, tsn)

    def put(self, request: Request, tsn: int, partial: bool = False) -> Resource:
        """
        summary: Update the details of an existing Cash Sale Refund

        description: |
            Attempt to update the details of an existing Nominal Ledger entry where the Transaction Type is for Cash
            Sale Refunds, returning a 404 if it doesn't exist

        path_params:
            tsn:
                description: The Transaction Sequence Number of the Cash Sale Refund record to be updated
                type: integer

        responses:
            200:
                description: The Cash Sale Refund record was updated successfully
            400: {}
            403: {}
            404: {}
        """
        return self._put(request, tsn, partial)
