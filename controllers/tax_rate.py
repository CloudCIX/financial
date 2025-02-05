# stdlib
from decimal import Decimal, InvalidOperation
from typing import Optional
# libs
from cloudcix_rest.controllers import ControllerBase
# local
from financial.models.tax_rate import TaxRate


__all__ = [
    'TaxRateListController',
    'TaxRateCreateController',
    'TaxRateUpdateController',
]


class TaxRateListController(ControllerBase):
    """
    Validates User data to filter a list of Tax Rate records
    """

    class Meta(ControllerBase.Meta):
        """
        Override some of the ControllerBase.Meta fields to make them more specific for this Controller
        """
        allowed_ordering = (
            'address_id',
            'id',
            'description',
            'percent',
        )
        search_fields = {
            'description': ControllerBase.DEFAULT_STRING_FILTER_OPERATORS,
            'id': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
            'percent': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
        }


class TaxRateCreateController(ControllerBase):
    """
    Validate User data to create a new Tax Rate record
    """

    class Meta:
        """
        Override some of the ControllerBase.Meta fields to make them more specific for this Controller
        """
        model = TaxRate
        validation_order = (
            'description',
            'percent',
        )

    def validate_description(self, description: Optional[str]) -> Optional[str]:
        """
        description: The type of Tax applied to a transaction, e.g. VAT, Customs Duty, etc.
        type: string
        """
        if description is None:
            description = ''
        description = str(description).strip()
        if len(description) == 0:
            return 'financial_tax_rate_create_101'
        if len(description) > self.get_field('description').max_length:
            return 'financial_tax_rate_create_102'
        tax_rate = TaxRate.objects.filter(
            description__iexact=description,
            address_id=self.request.user.address['id'],
        )
        if tax_rate.exists():
            return 'financial_tax_rate_create_103'
        self.cleaned_data['description'] = description
        return None

    def validate_percent(self, percent: Optional[str]) -> Optional[str]:
        """
        description: The rate of Tax to apply to a transaction
        type: string
        format: decimal
        """
        try:
            decimal_percent = Decimal(str(percent))
        except InvalidOperation:
            return 'financial_tax_rate_create_104'
        self.cleaned_data['percent'] = decimal_percent
        return None


class TaxRateUpdateController(ControllerBase):
    """
    Validate User data to update a Tax Rate record
    """

    class Meta:
        """
        Override some of the ControllerBase.Meta fields to make them more specific for this Controller
        """
        model = TaxRate
        validation_order = (
            'description',
            'percent',
        )

    def validate_description(self, description: Optional[str]) -> Optional[str]:
        """
        description: The type of Tax applied to a transaction, e.g. VAT, Customs Duty, etc.
        type: string
        """
        if description is None:
            description = ''
        description = str(description).strip()
        if len(description) == 0:
            return 'financial_tax_rate_update_101'
        if len(description) > self.get_field('description').max_length:
            return 'financial_tax_rate_update_102'
        tax_rate = TaxRate.objects.filter(
            description__iexact=description,
            address_id=self.request.user.address['id'],
        ).exclude(id=self._instance.pk)
        if tax_rate.exists():
            return 'financial_tax_rate_update_103'
        self.cleaned_data['description'] = description
        return None

    def validate_percent(self, percent: Optional[str]) -> Optional[str]:
        """
        description: The rate of Tax to apply to a transaction
        type: string
        format: decimal
        """
        try:
            decimal_percent = Decimal(str(percent))
        except InvalidOperation:
            return 'financial_tax_rate_update_104'
        self.cleaned_data['percent'] = decimal_percent
        return None
