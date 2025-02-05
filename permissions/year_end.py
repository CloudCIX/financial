# stdlib
from typing import Optional
# libs
from cloudcix_rest.exceptions import Http403
from rest_framework.request import Request
# local
from financial.models.nominal_ledger import NominalLedger


class Permissions:

    @staticmethod
    def create(request: Request) -> Optional[Http403]:
        """
        The request to create a Year End is valid if:
        - The requesting User's Member is self-managed
        """
        # The requesting User's Member is self-managed
        if not request.user.member['self_managed']:
            return Http403(error_code='financial_year_end_create_201')

        return None

    @staticmethod
    def delete(request: Request, obj: NominalLedger) -> Optional[Http403]:
        """
        The request to delete a Year End is valid if:
        - There are no Period Ends after the Year End's transaction date
        """
        # There are no Period Ends after the Year End's transaction date
        period_end = NominalLedger.objects.filter(
            address_id=request.user.address['id'],
            transaction_date__gt=obj.transaction_date,
        )
        if period_end.exists():
            return Http403(error_code='financial_year_end_delete_201')

        return None
