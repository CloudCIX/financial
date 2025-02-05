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
        The request to create an Account Sale Invoice is valid if:
        - The requesting User's Member is self-managed
        """
        # API User Allowance
        if request.user.id == 1:  # pragma: no cover
            return None

        # The requesting User's Member is self-managed
        if not request.user.member['self_managed']:
            return Http403(error_code='financial_account_sale_invoice_create_201')

        return None

    @staticmethod
    def read(request: Request, obj: NominalLedger, span) -> Optional[Http403]:
        """
        The request to read an Account Sale Invoice is valid if:
        - The User is reading an Account Sale Invoice from their own Address
        """
        # API User Allowance
        if request.user.id == 1:  # pragma: no cover
            return None

        # The User is reading an Account Sale Invoice from their own Address
        if request.user.address['id'] != obj.address_id:
            return Http403(error_code='financial_account_sale_invoice_read_201')

        return None

    @staticmethod
    def update(obj: NominalLedger) -> Optional[Http403]:
        """
        The request to update an Account Sale Invoice is valid if:
        - A contra transaction has not been made from the Account Sale Invoice
        - The Account Sale Invoice has not been processed by a period end
        - The Account Sale Invoice has not been allocated
        """
        # A contra transaction has not been made from the Account Sale Invoice
        if obj.contra_nominal_ledger is not None:
            return Http403(error_code='financial_account_sale_invoice_update_201')

        # The Account Sale Invoice has not been processed by a period end
        period_end = NominalLedger.period_end.filter(
            address_id=obj.address_id,
            transaction_date__gte=obj.transaction_date,
        )
        if period_end.exists():
            return Http403(error_code='financial_account_sale_invoice_update_202')

        # The Account Sale Invoice has not been allocated
        if obj.allocationdetail_set.all().exists():
            return Http403(error_code='financial_account_sale_invoice_update_203')

        return None

    @staticmethod
    def contra_create(request: Request) -> Optional[Http403]:
        """
        The request to create an Account Sale Invoice from an Account Purchase Invoice is valid if:
        - The requesting User's Member is self-managed
        """
        # The requesting User's Member is self-managed
        if not request.user.member['self_managed']:
            return Http403(error_code='financial_account_sale_invoice_contra_create_201')

        return None

    @staticmethod
    def contra_read(request: Request, obj: NominalLedger, span):
        """
        The request to read an Account Sale Invoice from another Address is valid if:
        - The Account Sale Invoice's Contra Address is the same as the requesting User's Address
        """
        # The Account Sale Invoice's Contra Address is the same as the requesting User's Address
        if obj.contra_address_id != request.user.address['id']:
            return Http403(error_code='financial_account_sale_invoice_contra_read_201')

        return None
