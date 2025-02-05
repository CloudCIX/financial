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
        The request to create a Cash Sale Invoice is valid if:
        - The requesting User's Member is self-managed
        """
        # The requesting User's Member is self-managed
        if not request.user.member['self_managed']:
            return Http403(error_code='financial_cash_sale_invoice_create_201')

        return None

    @staticmethod
    def read(request: Request, obj: NominalLedger, span) -> Optional[Http403]:
        """
        The request to read a Cash Sale Invoice is valid if:
        - The requesting User is reading a Cash Sale Invoice from their own Address
        """
        # The requesting User is reading a Cash Sale Invoice from their own Address
        if request.user.address['id'] != obj.address_id:
            return Http403(error_code='financial_cash_sale_invoice_read_201')

        return None

    @staticmethod
    def update(request: Request, obj: NominalLedger) -> Optional[Http403]:
        """
        The request to update a Cash Sale Invoice is valid if:
        - The Cash Sale Invoice does not have a contra transaction
        - The Cash Sale Invoice has not been processed by a period end
        - The Cash Sale Invoice has not been allocated
        """
        # The Cash Sale Invoice does not have a contra transaction
        if obj.contra_nominal_ledger is not None:
            return Http403(error_code='financial_cash_sale_invoice_update_201')

        # The Cash Sale Invoice has not been processed by a period end
        period_end = NominalLedger.period_end.filter(
            address_id=request.user.address['id'],
            transaction_date__gte=obj.transaction_date,
        )
        if period_end.exists():
            return Http403(error_code='financial_cash_sale_invoice_update_202')

        # The Cash Sale Invoice has not been allocated
        if obj.allocationdetail_set.all().exists():
            return Http403(error_code='financial_cash_sale_invoice_update_203')

        return None

    @staticmethod
    def contra_create(request: Request) -> Optional[Http403]:
        """
        The request to create a Cash Sale Invoice from a Cash Purchase Invoice is valid if:
        - The requesting User's Member is self managed
        """
        # The requesting User's Member is self managed
        if not request.user.member['self_managed']:
            return Http403(error_code='financial_cash_sale_invoice_contra_create_201')

        return None

    @staticmethod
    def contra_read(request: Request, obj: NominalLedger, span) -> Optional[Http403]:
        """
        The request to read a Cash Sale Invoice from another Address is valid if:
        - The Cash Sale invoice was made out to the requesting User's address
        """
        # The Cash Sale invoice was made out to the requesting User's address
        if request.user.address['id'] != obj.contra_address_id:
            return Http403(error_code='financial_cash_sale_invoice_contra_read_201')

        return None
