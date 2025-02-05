# stdlib
from typing import Optional
# libs
from cloudcix_rest.exceptions import Http403
from rest_framework.request import Request
# local
from financial.models.allocation import Allocation

__all__ = [
    'Permissions',
]


class Permissions:

    @staticmethod
    def create(request: Request) -> Optional[Http403]:
        """
        The request to create an Allocation is valid if:
        - The requesting User's Member is self-managed
        """
        # The requesting User's Member is self-managed
        if not request.user.member['self_managed']:
            return Http403(error_code='financial_allocation_create_201')
        return None

    @staticmethod
    def delete(request: Request, obj: Allocation) -> Optional[Http403]:
        """
        The request to delete a Allocation is valid if:
        - The Allocation belongs to the requesting User's Address
        """
        # The Allocation belongs to the requesting User's Address
        if request.user.address['id'] != obj.address_id:
            return Http403(error_code='financial_allocation_delete_201')
        return None
