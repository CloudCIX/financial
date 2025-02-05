# stdlib
from typing import Optional
# libs
from cloudcix_rest.controllers import ControllerBase
# local
from financial.models import PaymentMethod


__all__ = [
    'PaymentMethodCreateController',
    'PaymentMethodListController',
    'PaymentMethodUpdateController',
]


class PaymentMethodListController(ControllerBase):

    """
    Validates User data to filter a list of Payment Method records
    """

    class Meta(ControllerBase.Meta):
        """
        Override some of the ControllerBase.Meta fields to make them more specific for this Controller
        """
        allowed_ordering = (
            'description',
            'id',
        )
        search_fields = {
            'description': ControllerBase.DEFAULT_STRING_FILTER_OPERATORS,
            'id': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
        }


class PaymentMethodCreateController(ControllerBase):
    """
    Validate User data to create a new Payment Method record
    """

    class Meta:
        """
        Override some of the ControllerBase.Meta fields to make them more specific for this Controller
        """
        model = PaymentMethod
        validation_order = (
            'description',
        )

    def validate_description(self, description: Optional[str]) -> Optional[str]:
        """
        description: How a payment will be made, e.g. cash, cheque, credit card, etc.
        type: string
        """
        if description is None:
            description = ''
        description = str(description).strip()
        if len(description) == 0:
            return 'financial_payment_method_create_101'
        if len(description) > self.get_field('description').max_length:
            return 'financial_payment_method_create_102'
        obj = PaymentMethod.objects.filter(
            member_id=self.request.user.member['id'],
            description=description,
        )
        if obj.exists():
            return 'financial_payment_method_create_103'
        self.cleaned_data['description'] = description
        return None


class PaymentMethodUpdateController(ControllerBase):
    """
    Validate User data to update a Payment Method record
    """

    class Meta:
        """
        Override some of the ControllerBase.Meta fields to make them more specific for this Controller
        """
        model = PaymentMethod
        validation_order = (
            'description',
        )

    def validate_description(self, description: Optional[str]) -> Optional[str]:
        """
        description: How a payment will be made, e.g. cash, cheque, credit card, etc.
        type: string
        """
        if description is None:
            description = ''
        description = str(description).strip()
        if len(description) == 0:
            return 'financial_payment_method_update_101'
        if len(description) > self.get_field('description').max_length:
            return 'financial_payment_method_update_102'
        obj = PaymentMethod.objects.exclude(id=self._instance.pk).filter(
            member_id=self.request.user.member['id'],
            description=description,
        )
        if obj.exists():
            return 'financial_payment_method_update_103'
        self.cleaned_data['description'] = description
        return None
