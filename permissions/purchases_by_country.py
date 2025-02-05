# stdlib
from typing import Optional
# libs
from cloudcix.api.membership import Membership
from cloudcix_rest.exceptions import Http403
from rest_framework.request import Request


class Permissions:

    @staticmethod
    def list(request: Request, address_id: int, span) -> Optional[Http403]:
        """
        The request to list the data for a Purchases by Country is valid if:
        - The requesting User is listing data from their own Address
        - The requesting User is Global Active and is listing data from another Address in their Member
        """
        if address_id is None:
            return None

        # The requesting User is listing data from their own Address
        if request.user.address['id'] == address_id:
            return None

        # The requesting User is Global Active and is listing data from another Address in their Member
        if not request.user.global_active:
            return Http403(error_code='financial_purchases_by_country_list_201')

        response = Membership.address.read(
            token=request.user.token,
            pk=address_id,
            span=span,
        )
        if response.status_code != 200 or response.json()['content']['member']['id'] != request.user.member['id']:
            return Http403(error_code='financial_purchases_by_country_list_202')

        return None
