"""
A base class for use when listing data for Financial Statements that analyse entries on the Nominal Ledger
These Financial Statements include Balance Sheets, Profit and Loss accounts, Trial Balances, and VIES
"""

# stdlib
from datetime import date, datetime
from typing import cast, Dict, Optional
# libs
from cloudcix_rest.controllers import ControllerBase


__all__ = [
    'TransactionsByCountryBase',
]


class TransactionsByCountryBase(ControllerBase):
    """
    This class is for holding validation methods for controllers that are used in displaying and analysing entries from
    the Nominal Ledger. In the implementations of these controllers we just need to specify a validation order and
    error codes
    """
    error_codes: Dict[str, str] = dict()

    def validate_address_id(self, address_id: Optional[int]) -> Optional[str]:
        """
        description: The id of an Address in the User's Member
        type: integer
        optional: true
        """
        if address_id is not None:
            try:
                address_id = int(cast(int, address_id))
            except (TypeError, ValueError):
                return self.error_codes.get('address_id__not_int')

        self.cleaned_data['address_id'] = address_id
        return None

    def validate_start_date(self, start_date: Optional[str]) -> Optional[str]:
        """
        description: |
            Transactions created on and after this date that should by used in analysis. Default is `1900-01-01`
        type: string
        """
        if start_date is not None:
            try:
                start = datetime.strptime(str(start_date).split('T')[0], '%Y-%m-%d').date()
            except (TypeError, ValueError):
                return self.error_codes.get('start_date__not_isoformat')
            self.cleaned_data['start_date'] = start
            return None

        self.cleaned_data['start_date'] = date(1900, 1, 1)
        return None

    def validate_finish_date(self, finish_date: Optional[str]) -> Optional[str]:
        """
        description: |
            Transactions created on and before this date that should by used in analysis. Default is `2999-12-31`
        type: string
        """
        if finish_date is not None:
            try:
                finish = datetime.strptime(str(finish_date).split('T')[0], '%Y-%m-%d').date()
            except (TypeError, ValueError):
                return self.error_codes.get('finish_date__not_isoformat')

            start_date = self.cleaned_data.get('start_date')
            if start_date is not None and start_date > finish:
                return self.error_codes.get('finish_date__before_start_date')

            self.cleaned_data['finish_date'] = finish
            return None

        self.cleaned_data['finish_date'] = date(2999, 12, 31)
        return None
