"""
A base class for use when listing data for Financial Statements that analyse entries on the Nominal Ledger
These Financial Statements include Balance Sheets, Profit and Loss accounts, Trial Balances, and VIES
"""

# stdlib
from datetime import datetime
from typing import cast, Dict, Optional
# libs
from cloudcix_rest.controllers import ControllerBase


__all__ = [
    'NominalLedgerBase',
]


class NominalLedgerBase(ControllerBase):
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
                return self.error_codes['address_id__not_int']

        self.cleaned_data['address_id'] = address_id
        return None

    def validate_date(self, transaction_date: Optional[str]) -> Optional[str]:
        """
        description: The date that the financial statement will be created for
        type: string
        """
        try:
            date = datetime.strptime(str(transaction_date).split('T')[0], '%Y-%m-%d').date()
        except (TypeError, ValueError):
            return self.error_codes['date__not_isoformat']

        self.cleaned_data['date'] = date
        return None

    def validate_start_date(self, transaction_date: Optional[str]) -> Optional[str]:
        """
        description: The date of the first transactions to include in a financial statement
        type: string
        """
        try:
            start_date = datetime.strptime(str(transaction_date).split('T')[0], '%Y-%m-%d').date()
        except (TypeError, ValueError):
            return self.error_codes['start_date__not_isoformat']

        self.cleaned_data['start_date'] = start_date
        return None

    def validate_end_date(self, transaction_date: Optional[str]) -> Optional[str]:
        """
        description: The date of the last transactions to include in a financial statement
        type: string
        """
        try:
            end_date = datetime.strptime(str(transaction_date).split('T')[0], '%Y-%m-%d').date()
        except (TypeError, ValueError):
            return self.error_codes['end_date__not_isoformat']

        start_date = self.cleaned_data.get('start_date')
        if start_date is not None and start_date >= end_date:
            return self.error_codes['end_date__before_start_date']

        self.cleaned_data['end_date'] = end_date
        return None
