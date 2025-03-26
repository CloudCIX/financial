# stdlib
from datetime import date
from typing import Optional
# libs
from cloudcix_rest.controllers import ControllerBase
# local
from financial.controllers.transaction_mixin import FinancialException, TransactionMixin


__all__ = [
    'SalesByCountryListController',
]


class SalesByCountryListController(ControllerBase, TransactionMixin):
    """
    Validate User data used to specify which records will be used when calculating Sales by Country totals.
    """

    class Meta(ControllerBase.Meta):
        """
        Override some of the ControllerBase.Meta fields to make them more specific for this Controller
        """
        validation_order = (
            'address_id',
            'start_date',
            'finish_date',
        )

    def validate_address_id(self, address_id: Optional[int]) -> Optional[str]:
        """
        description: |
            The address_id to generate the Sales By Country to. If not sent it will default to what the requesting
            User has permission for.
        type: string
        required: false
        """
        if address_id is not None:
            try:
                address_id = self._validate_integer(address_id, 'financial_sales_by_country_list_101')
            except FinancialException as e:
                return e.args[0]

        self.cleaned_data['address_id'] = address_id
        return None

    def validate_start_date(self, start_date: Optional[str]) -> Optional[str]:
        """
        description:  |
            Transactions created on and after this date that should by used in analysis. Default is `1900-01-01`
        type: string
        required: false
        """
        if start_date is not None:
            try:
                start_date = self._validate_date(start_date, 'financial_sales_by_country_list_102')
            except FinancialException as e:
                return e.args[0]
            self.cleaned_data['start_date'] = start_date
            return None

        self.cleaned_data['start_date'] = date(1900, 1, 1)
        return None

    def validate_finish_date(self, finish_date: Optional[str]) -> Optional[str]:
        """
        description: |
            Transactions created on and before this date that should by used in analysis. Default is `2999-12-31`
        type: string
        required: false
        """
        if finish_date is not None:
            try:
                finish = self._validate_date(finish_date, 'financial_sales_by_country_list_103')
            except FinancialException as e:
                return e.args[0]
        else:
            finish = date(2999, 12, 31)

        if 'start_date' not in self.cleaned_data:
            return None
        try:
            self._validate_start_end_dates(
                self.cleaned_data['start_date'],
                finish,
                'financial_sales_by_country_list_104',
            )
        except FinancialException as e:
            return e.args[0]

        self.cleaned_data['finish_date'] = finish
        return None
