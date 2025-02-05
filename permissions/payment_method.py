# stdlib
from typing import Optional
# libs
from cloudcix_rest.exceptions import Http403
from rest_framework.request import Request
# local
from financial.models import PaymentMethod


__all__ = [
    'Permissions',
]


class Permissions:

    @staticmethod
    def create(request: Request) -> Optional[Http403]:
        """
        The request to create a Payment Method is valid if:
        - The requesting User's Member is self-managed
        - The requesting User is an administrator
        """
        # The requesting User's Member is self-managed
        if not request.user.member['self_managed']:
            return Http403(error_code='financial_payment_method_create_201')

        # The requesting User is an administrator
        if not request.user.administrator:
            return Http403(error_code='financial_payment_method_create_202')

        return None

    @staticmethod
    def update(request: Request) -> Optional[Http403]:
        """
        The request to update a Payment Method is valid if:
        - The requesting User's Member is self-managed
        - The requesting User is an administrator
        """
        # The requesting User's Member is self-managed
        if not request.user.member['self_managed']:
            return Http403(error_code='financial_payment_method_update_201')

        # The requesting User is an administrator
        if not request.user.administrator:
            return Http403(error_code='financial_payment_method_update_202')

        return None

    @staticmethod
    def delete(request: Request) -> Optional[Http403]:
        """
        The request to delete a Payment Method is valid if:
        - The requesting User's Member is self-managed
        - The requesting User is an administrator
        - The Payment Method is not the only Payment Method in the Member
        """
        # The requesting User's Member is self-managed
        if not request.user.member['self_managed']:
            return Http403(error_code='financial_payment_method_delete_201')

        # The requesting User is an administrator
        if not request.user.administrator:
            return Http403(error_code='financial_payment_method_delete_202')

        # The Payment Method is not the only Payment Method in the Member
        if PaymentMethod.objects.filter(
            member_id=request.user.member['id'],
        ).count() == 1:
            return Http403(error_code='financial_payment_method_delete_203')

        return None
