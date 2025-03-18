# stdlib
from typing import Optional
# libs
from cloudcix_rest.controllers import ControllerBase
# local
from financial.controllers.transaction_mixin import FinancialException, TransactionMixin

__all__ = [
    'BalanceSheetListController',
]


class BalanceSheetListController(ControllerBase, TransactionMixin):
    """
    Validate User data used to specify which records will be used when listing Nominal Account totals for a Balance
    Sheet
    """

    class Meta(ControllerBase.Meta):
        """
        Override some of the ControllerBase.Meta fields to make them more specific for this Controller
        """
        validation_order = (
            'address_id',
            'date',
        )

    def validate_address_id(self, address_id: Optional[int]) -> Optional[str]:
        """
        description: The address_id to generate the Balance Sheet statement for.
        type: string
        """
        try:
            address_id = self._validate_integer(address_id, 'financial_balance_sheet_list_101')
        except FinancialException as e:
            return e.args[0]

        self.cleaned_data['address_id'] = address_id
        return None

    def validate_date(self, date: Optional[str]) -> Optional[str]:
        """
        description: The date that the Balance Sheet statement is to be generated on.
        type: string
        """
        try:
            date = self._validate_date(date, 'financial_balance_sheet_list_102')
        except FinancialException as e:
            return e.args[0]

        self.cleaned_data['date'] = date
        return None
