# stdlib
from typing import Optional
# libs
from cloudcix_rest.exceptions import Http403
from rest_framework.request import Request


__all__ = [
    'Permissions',
]


class Permissions:

    @staticmethod
    def create(request: Request) -> Optional[Http403]:
        """
        The request to create a Nominal Contra is valid if:
        - The requesting User's Member is self-managed
        - The requesting User is an administrator
        """
        # The requesting User's Member is self-managed
        if not request.user.member['self_managed']:
            return Http403(error_code='financial_nominal_contra_create_201')

        # The requesting User is an administrator
        if not request.user.administrator:
            return Http403(error_code='financial_nominal_contra_create_202')

        return None

    @staticmethod
    def update(request: Request):
        """
        The request to update a Nominal Contra is valid if:
        - The requesting User's Member is self-managed
        - The requesting User is an administrator
        """
        # The requesting User's Member is self-managed
        if not request.user.member['self_managed']:
            return Http403(error_code='financial_nominal_contra_update_201')

        # The requesting User is an administrator
        if not request.user.administrator:
            return Http403(error_code='financial_nominal_contra_update_202')

        return None

    @staticmethod
    def delete(request: Request):
        """
        The request to delete a Nominal Contra is valid if:
        - The requesting User's Member is self-managed
        - The requesting User is an administrator
        """
        # The requesting User's Member is self-managed
        if not request.user.member['self_managed']:
            return Http403(error_code='financial_nominal_contra_delete_201')

        # The requesting User is an administrator
        if not request.user.administrator:
            return Http403(error_code='financial_nominal_contra_delete_202')

        return None
