# stdlib
from typing import cast, Optional
# libs
from cloudcix_rest.controllers import ControllerBase
# local
from financial.models.global_nominal_account import GlobalNominalAccount
from financial.models.nominal_contra import NominalContra
from financial.models.payment_method import PaymentMethod


__all__ = [
    'NominalContraListController',
    'NominalContraCreateController',
    'NominalContraUpdateController',
]

CONTRA_ACCOUNT_NUMBER_RANGE = range(1000, 3000)
TRANSACTION_TYPES = [
    10000, 10001, 10004, 10006, 10007,  # Purchases
    11000, 11001, 11004, 11006, 11007,  # Sales
]


class NominalContraListController(ControllerBase):
    """
    Validates User data to filter a list of Nominal Contra records
    """

    class Meta(ControllerBase.Meta):
        """
        Override some of the ControllerBase.Meta fields to make them more specific for this Controller
        """
        allowed_ordering = (
            'global_nominal_account_id',
            'global_nominal_account__nominal_account_number',
            'id',
            'payment_method_id',
            'payment_method__description',
            'transaction_type_id',
        )
        search_fields = {
            'global_nominal_account_id': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
            'global_nominal_account__nominal_account_number': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
            'id': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
            'payment_method_id': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
            'payment_method__description': ControllerBase.DEFAULT_STRING_FILTER_OPERATORS,
            'transaction_type_id': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
        }


class NominalContraCreateController(ControllerBase):
    """
    Validate User data to create a new Nominal Contra record
    """

    class Meta(ControllerBase.Meta):
        """
        Override some of the ControllerBase.Meta fields to make them more specific for this Controller
        """
        model = NominalContra
        validation_order = (
            'global_nominal_account_id',
            'payment_method_id',
            'transaction_type_id',
        )

    def validate_global_nominal_account_id(self, global_nominal_account_id: Optional[int]) -> Optional[str]:
        """
        description: |
            The id of the Global Nominal Account that will be used to balance the transactions for a given Transaction
            Type and Payment Method pair
        type: integer
        """
        try:
            obj = GlobalNominalAccount.objects.get(
                id=int(cast(int, global_nominal_account_id)),
                member_id=self.request.user.member['id'],
            )
        except (TypeError, ValueError):
            return 'financial_nominal_contra_create_101'
        except GlobalNominalAccount.DoesNotExist:
            return 'financial_nominal_contra_create_102'
        if obj.nominal_account_number not in CONTRA_ACCOUNT_NUMBER_RANGE:
            return 'financial_nominal_contra_create_103'
        self.cleaned_data['global_nominal_account'] = obj
        return None

    def validate_payment_method_id(self, payment_method_id: Optional[int]) -> Optional[str]:
        """
        description: |
            The id of the Payment Method which, along with the Transaction Type id, will determine which Nominal Account
            will be used to balance a transaction
        type: integer
        """
        try:
            obj = PaymentMethod.objects.get(
                id=int(cast(int, payment_method_id)),
                member_id=self.request.user.member['id'],
            )
        except (TypeError, ValueError):
            return 'financial_nominal_contra_create_104'
        except PaymentMethod.DoesNotExist:
            return 'financial_nominal_contra_create_105'
        self.cleaned_data['payment_method'] = obj
        return None

    def validate_transaction_type_id(self, transaction_type_id: Optional[int]) -> Optional[str]:
        """
        description: |
            The id of the Transaction Type which, along with the Payment Method id, will determine which Nominal Account
            will be used to balance a transaction
        type: integer
        """
        try:
            transaction_type_id = int(cast(int, transaction_type_id))
        except (TypeError, ValueError):
            return 'financial_nominal_contra_create_106'
        if transaction_type_id not in TRANSACTION_TYPES:
            return 'financial_nominal_contra_create_107'
        payment_method = self.cleaned_data.get('payment_method')
        if payment_method is None:
            # We can't check if the Payment Method and Transaction Type are unique together so just return nothing
            return None
        obj = NominalContra.objects.filter(
            payment_method=payment_method,
            transaction_type_id=transaction_type_id,
        )
        if obj.exists():
            return 'financial_nominal_contra_create_108'
        self.cleaned_data['transaction_type_id'] = transaction_type_id
        return None


class NominalContraUpdateController(ControllerBase):
    """
    Validate User data to update a Nominal Contra record
    """

    class Meta(ControllerBase.Meta):
        """
        Override some of the ControllerBase.Meta fields to make them more specific for this Controller
        """
        model = NominalContra
        validation_order = (
            'global_nominal_account_id',
            'payment_method_id',
            'transaction_type_id',
        )

    def validate_global_nominal_account_id(self, global_nominal_account_id: Optional[int]) -> Optional[str]:
        """
        description: |
            The id of the Global Nominal Account that will be used to balance the transactions for a given Transaction
            Type and Payment Method pair
        type: integer
        """
        try:
            obj = GlobalNominalAccount.objects.get(
                id=int(cast(int, global_nominal_account_id)),
                member_id=self.request.user.member['id'],
            )
        except (TypeError, ValueError):
            return 'financial_nominal_contra_update_101'
        except GlobalNominalAccount.DoesNotExist:
            return 'financial_nominal_contra_update_102'
        if obj.nominal_account_number not in CONTRA_ACCOUNT_NUMBER_RANGE:
            return 'financial_nominal_contra_update_103'
        self.cleaned_data['global_nominal_account'] = obj
        return None

    def validate_payment_method_id(self, payment_method_id: Optional[int]) -> Optional[str]:
        """
        description: |
            The id of the Payment Method which, along with the Transaction Type id, will determine which Nominal Account
            will be used to balance a transaction
        type: integer
        """
        try:
            obj = PaymentMethod.objects.get(
                id=int(cast(int, payment_method_id)),
                member_id=self.request.user.member['id'],
            )
        except (TypeError, ValueError):
            return 'financial_nominal_contra_update_104'
        except PaymentMethod.DoesNotExist:
            return 'financial_nominal_contra_update_105'
        self.cleaned_data['payment_method'] = obj
        return None

    def validate_transaction_type_id(self, transaction_type_id: Optional[int]) -> Optional[str]:
        """
        description: |
            The id of the Transaction Type which, along with the Payment Method id, will determine which Nominal Account
            will be used to balance a transaction
        type: integer
        """
        try:
            transaction_type_id = int(cast(int, transaction_type_id))
        except (TypeError, ValueError):
            return 'financial_nominal_contra_update_106'
        if transaction_type_id not in TRANSACTION_TYPES:
            return 'financial_nominal_contra_update_107'
        self.cleaned_data['transaction_type_id'] = transaction_type_id
        return None

    def is_valid(self) -> bool:
        is_valid = super(NominalContraUpdateController, self).is_valid()
        if not is_valid:
            return is_valid

        # Make sure the Transaction Type and Payment Method pair are unique
        if 'payment_method' in self.cleaned_data or 'transaction_type_id' in self.cleaned_data:
            payment_method = self.cleaned_data.get('payment_method', self._instance.payment_method)
            transaction_type_id = self.cleaned_data.get('transaction_type_id', self._instance.transaction_type_id)
            obj = NominalContra.objects.filter(
                payment_method=payment_method,
                transaction_type_id=transaction_type_id,
            ).exclude(id=self._instance.id)
            if obj.exists():
                self._errors['transaction_type_id'] = 'financial_nominal_contra_update_108'
                is_valid = False

        return is_valid
