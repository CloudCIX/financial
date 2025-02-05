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
        The request to create a Cash Sale Refund is valid if:
        - The requesting User's Member is self-managed
        """
        # The requesting User's Member is self-managed
        if not request.user.member['self_managed']:
            return Http403(error_code='financial_cash_sale_refund_create_201')

        return None

    @staticmethod
    def update(obj: NominalLedger) -> Optional[Http403]:
        """
        The request to update a Cash Sale Refund is valid if:
        - The Cash Sale Refund has not been processed by a period end
        """
        # The Cash Sale Refund has not been processed by a period end
        period_end = NominalLedger.period_end.filter(
            address_id=obj.address_id,
            transaction_date__gte=obj.transaction_date,
        )
        if period_end.exists():
            return Http403(error_code='financial_cash_sale_refund_update_201')

        return None
