# stdlib
from typing import Optional
# libs
from cloudcix_rest.exceptions import Http403
from django.db.models import Q
from rest_framework.request import Request
# local
from financial import reserved_accounts
from financial.models.global_nominal_account import GlobalNominalAccount
from financial.models.nominal_ledger import NominalLedger


__all__ = [
    'Permissions',
]


class Permissions:

    @staticmethod
    def create(request: Request) -> Optional[Http403]:
        """
        The request to create a Global Nominal Account is valid if:
        - The requesting User's Member is self-managed
        - The requesting User is an administrator
        """
        # The requesting User's Member is self-managed
        if not request.user.member['self_managed']:
            return Http403(error_code='financial_global_nominal_account_create_201')

        # The requesting User is an administrator
        if not request.user.administrator:
            return Http403(error_code='financial_global_nominal_account_create_202')

        return None

    @staticmethod
    def update(request: Request, address_id: Optional[int]) -> Optional[str]:
        """
        The request to update a Nominal Account is valid if:
        - The requesting User is an administrator
        - The requesting User updating one of their Address Nominal Accounts
        """
        # The requesting User is an administrator
        if not request.user.administrator:
            return Http403(error_code='financial_global_nominal_account_update_201')

        if address_id is not None:
            # The requesting User is updating one of their Address Nominal Accounts
            if address_id != request.user.address['id']:
                return Http403(error_code='financial_global_nominal_account_update_202')

        return None

    @staticmethod
    def delete(request: Request, obj: GlobalNominalAccount) -> Optional[str]:
        """
        The request to delete a Global Nominal Account is valid if:
        - The requesting User's Member is self-managed
        - The requesting User is an administrator
        - The requesting User is deleting an account from their Member
        - The Account is not one of the Reserved Accounts
        - The Account is not in use
        """
        # The requesting User's Member is self-managed
        if not request.user.member['self_managed']:
            return Http403(error_code='financial_global_nominal_account_delete_201')

        # The requesting User is an administrator
        if not request.user.administrator:
            return Http403(error_code='financial_global_nominal_account_delete_202')

        # The requesting User is deleting an account from their Member
        if request.user.member['id'] != obj.member_id:
            return Http403(error_code='financial_global_nominal_account_delete_203')

        # The Account is not one of the Reserved Accounts
        reserved_account_numbers = [
            getattr(reserved_accounts, attr)
            for attr in dir(reserved_accounts) if not attr.startswith('__')
        ]
        if obj.nominal_account_number in reserved_account_numbers:
            return Http403(error_code='financial_global_nominal_account_delete_204')

        # The Account is not in use
        address_ids = [account.address_id for account in obj.address_nominal_accounts.all()]
        account_number_filter = Q(debits__nominal_account_number=obj.nominal_account_number)
        account_number_filter |= Q(credits__nominal_account_number=obj.nominal_account_number)
        transactions = NominalLedger.objects.filter(
            account_number_filter,
            address_id__in=address_ids,
        )
        if transactions.exists():
            return Http403(error_code='financial_global_nominal_account_delete_205')

        return None
