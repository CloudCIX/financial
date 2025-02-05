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
    def list(request: Request) -> Optional[Http403]:
        """
        The request to list a Return of Trading Details report is valid if:
        - The requesting User's Address is in Ireland
        """
        # The requesting User's Address is in Ireland
        if request.user.address['country_id'] != 372:
            return Http403(error_code='financial_rtd_list_201')

        return None
