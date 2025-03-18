# stdlib
from typing import Optional
# libs
from cloudcix_rest.controllers import ControllerBase
# local
from financial.controllers.transaction_mixin import FinancialException, TransactionMixin


__all__ = [
    'RTDListController',
]


class RTDListController(ControllerBase, TransactionMixin):
    """
    Validate User data to list Nominal Ledger data for an Return of Trading Details report
    """

    class Meta(ControllerBase.Meta):
        """
        Override some of the ControllerBase.Meta fields to make them more specific for this Controller
        """
        validation_order = (
            'start_date',
            'end_date',
        )

    def validate_start_date(self, start_date: Optional[str]) -> Optional[str]:
        """
        description: The start date of the transactions required to create a Return of Trading Details report
        type: string
        """
        try:
            start_date = self._validate_date(start_date, 'financial_rtd_list_101')
        except FinancialException as e:
            return e.args[0]

        self.cleaned_data['start_date'] = start_date
        return None

    def validate_end_date(self, end_date: Optional[str]) -> Optional[str]:
        """
        description: The end date of the transactions required to create a Return of Trading Details report
        type: string
        """
        try:
            end_date = self._validate_date(end_date, 'financial_rtd_list_102')
        except FinancialException as e:
            return e.args[0]
        if 'start_date' not in self.cleaned_data:
            return None
        try:
            self._validate_start_end_dates(self.cleaned_data['start_date'], end_date, 'financial_rtd_list_103')
        except FinancialException as e:
            return e.args[0]

        self.cleaned_data['end_date'] = end_date
        return None
