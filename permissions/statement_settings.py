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
    def read(request: Request, address_id: int) -> Optional[Http403]:
        """
        The request to update a Statement Setting is valid if:
        - The requesting User's Address is the same as the address_id
        """
        if request.user.id == 1:
            return None
        # The requesting User's Address is the same as the address_id
        if request.user.address['id'] != address_id:
            return Http403(error_code='financial_statement_settings_read_201')

        return None

    @staticmethod
    def update(request: Request, address_id: int) -> Optional[Http403]:
        """
        The request to update a Statement Setting is valid if:
        - The requesting User's Member is self-managed
        - The requesting User's Address is the same as the address_id
        """
        # The requesting User's Member is self-managed
        if not request.user.member['self_managed']:
            return Http403(error_code='financial_statement_settings_update_201')
        # The requesting User's Address is the same as the address_id
        if request.user.address['id'] != address_id:
            return Http403(error_code='financial_statement_settings_update_202')

        return None
