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
        The request to create a Journal Entry is valid if:
        - The requesting User's Member is self-managed
        """
        # The requesting User's Member is self-managed
        if not request.user.member['self_managed']:
            return Http403(error_code='financial_journal_entry_create_201')

        return None

    @staticmethod
    def update(request: Request, obj: NominalLedger) -> Optional[Http403]:
        """
        The request to update a Journal Entry is valid if:
        - The Journal Entry has not been processed by a period end
        """
        # The Journal Entry has not been processed by a period end
        period_end = NominalLedger.period_end.filter(
            address_id=request.user.address['id'],
            transaction_date__gte=obj.transaction_date,
        )
        if period_end.exists():
            return Http403(error_code='financial_journal_entry_update_201')

        return None
