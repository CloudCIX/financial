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
        The request to create a Period End is valid if:
        - The requesting User's Member is self-managed
        """
        # The requesting User's Member is self-managed
        if not request.user.member['self_managed']:
            return Http403(error_code='financial_period_end_create_201')

        return None

    @staticmethod
    def delete(request: Request, obj: NominalLedger) -> Optional[Http403]:
        """
        The request to delete a Period End is valid if:
        - It is the most recent Period End
        - The Period End is not associated with a Year End
        """
        # It is the most recent Period End
        period_end = NominalLedger.period_end.filter(
            address_id=request.user.address['id'],
            transaction_date__gte=obj.transaction_date,
        ).exclude(
            id=obj.id,
        )
        if period_end.exists():
            return Http403(error_code='financial_period_end_delete_201')

        # The Period End is not associated with a Year End
        year_end = NominalLedger.year_ends.filter(
            address_id=request.user.address['id'],
            transaction_date=obj.transaction_date,
        )
        if year_end.exists():
            return Http403(error_code='financial_period_end_delete_202')

        return None
