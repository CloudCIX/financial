# stdlib
from typing import Optional
# libs
from cloudcix_rest.controllers import ControllerBase
# local
from financial.controllers.transaction_mixin import FinancialException, TransactionMixin

__all__ = [
    'ProfitAndLossListController',
]


class ProfitAndLossListController(ControllerBase, TransactionMixin):
    """
    Validate User data used to specify which records will be used when listing Nominal Account totals for a Profit and
    Loss sheet
    """

    class Meta(ControllerBase.Meta):
        """
        Override some of the ControllerBase.Meta fields to make them more specific for this controller
        """
        validation_order = (
            'address_id',
            'start_date',
            'end_date',
        )

    def validate_address_id(self, address_id: Optional[int]) -> Optional[str]:
        """
        description: The address_id to generate the Profit and Loss statement for.
        type: string
        """
        try:
            address_id = self._validate_integer(address_id, 'financial_profit_and_loss_list_101')
        except FinancialException as e:
            return e.args[0]

        self.cleaned_data['address_id'] = address_id
        return None

    def validate_start_date(self, start_date: Optional[str]) -> Optional[str]:
        """
        description: The start date of the transactions required to generate the Profit and Loss statement
        type: string
        """
        try:
            start_date = self._validate_date(start_date, 'financial_profit_and_loss_list_102')
        except FinancialException as e:
            return e.args[0]

        self.cleaned_data['start_date'] = start_date
        return None

    def validate_end_date(self, end_date: Optional[str]) -> Optional[str]:
        """
        description: The end date of the transactions required to generate the Profit and Loss statement
        type: string
        """
        try:
            end_date = self._validate_date(end_date, 'financial_profit_and_loss_list_103')
        except FinancialException as e:
            return e.args[0]
        if 'start_date' not in self.cleaned_data:
            return None
        try:
            self._validate_start_end_dates(
                self.cleaned_data['start_date'],
                end_date,
                'financial_profit_and_loss_list_104',
            )
        except FinancialException as e:
            return e.args[0]

        self.cleaned_data['end_date'] = end_date
        return None
