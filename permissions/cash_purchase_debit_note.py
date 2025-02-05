# stdlib
from typing import Optional
# libs
from cloudcix_rest.exceptions import Http403
from rest_framework.request import Request
# local
from financial.models.nominal_ledger import NominalLedger


__all__ = [
    'Permissions',
]


class Permissions:

    @staticmethod
    def create(request: Request) -> Optional[Http403]:
        """
        The request to create an Cash Purchase Debit Note is valid if:
        - The requesting User's Member is self-managed
        """
        # The requesting User's Member is self-managed
        if not request.user.member['self_managed']:
            return Http403(error_code='financial_cash_purchase_debit_note_create_201')

        return None

    @staticmethod
    def read(request: Request, obj: NominalLedger, span):
        """
        The request to read a Cash Purchase Debit Note is valid if:
        - The requesting User is reading a Cash Purchase Debit Note from their own Address
        """
        # The requesting User is reading a Cash Purchase Debit Note from their own Address
        if request.user.address['id'] != obj.address_id:
            return Http403(error_code='financial_cash_purchase_debit_note_read_201')

        return None

    @staticmethod
    def update(request: Request, obj: NominalLedger):
        """
        The request to update a Cash Purchase Debit Note is valid if:
        - A contra transaction has not been made from the Cash Purchase Debit Note
        - The Cash Purchase Debit Note has not been processed by a period end
        - The Cash Purchase Debit Note has not been allocated
        """
        # A contra transaction has not been made from the Cash Purchase Debit Note
        if obj.contra_nominal_ledger is not None:
            return Http403(error_code='financial_cash_purchase_debit_note_update_201')

        # The Cash Purchase Debit Note has not been processed by a period end
        period_end = NominalLedger.period_end.filter(
            address_id=request.user.address['id'],
            transaction_date__gte=obj.transaction_date,
        )
        if period_end.exists():
            return Http403(error_code='financial_cash_purchase_debit_note_update_202')

        # The Cash Purchase Debit Note has not been allocated
        if obj.allocationdetail_set.all().exists():
            return Http403(error_code='financial_cash_purchase_debit_note_update_203')

        return None

    @staticmethod
    def contra_create(request: Request):
        """
        The request to create a Cash Purchase Debit Note from a Cash Sale Credit Note is valid if:
        - The requesting User's Member is self-managed
        """
        # The requesting User's Member is self-managed
        if not request.user.member['self_managed']:
            return Http403(error_code='financial_cash_purchase_debit_note_contra_create_201')

        return None

    @staticmethod
    def contra_read(request: Request, obj: NominalLedger, span):
        """
        The request to read a Cash Purchase Debit Note from another Address is valid if:
        - The requesting User is reading a Cash Purchase Debit Note made out to their own Address
        """
        # The requesting User is reading a Cash Purchase Debit Note made out to their own Address
        if request.user.address['id'] != obj.contra_address_id:
            return Http403(error_code='financial_cash_purchase_debit_note_contra_read_201')

        return None
