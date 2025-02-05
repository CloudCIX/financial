# stdlib
from typing import cast, Optional
# libs
from cloudcix.api.membership import Membership
from cloudcix_rest.controllers import ControllerBase
# local
from financial.models import AddressNominalAccount, GlobalNominalAccount, NominalAccountType


FIXED_ASSETS_ACCOUNT = 1
SALES_ACCOUNT = 4000
PURCHASES_ACCOUNT = 5000
DIRECT_EXPENSES_ACCOUNT = 6000
OVERHEADS_ACCOUNT = 7000


__all__ = [
    'GlobalNominalAccountListController',
    'GlobalNominalAccountCreateController',
    'GlobalNominalAccountUpdateController',
]


class GlobalNominalAccountListController(ControllerBase):
    """
    Validates User data to filter a list of Nominal Account records
    """

    class Meta(ControllerBase.Meta):
        """
        Override some of the ControllerBase.Meta fields to make them more specific for this Controller
        """
        allowed_ordering = (
            'description',
            'external_reference',
            'nominal_account_number',
        )
        search_fields = {
            'description': ControllerBase.DEFAULT_STRING_FILTER_OPERATORS,
            'external_reference': ('icontains', 'iendswith', 'in', 'isnull', 'istartswith'),
            'id': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
            'nominal_account_number': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
            'nominal_account_type_id': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
        }


class GlobalNominalAccountCreateController(ControllerBase):
    """
    Validate User data to create a new Global Nominal Account record
    """

    class Meta:
        """
        Override some of the ControllerBase.Meta fields to make them more specific for this Controller
        """
        model = GlobalNominalAccount
        validation_order = (
            'description',
            'nominal_account_type_id',
            'nominal_account_number',
            'external_reference',
            'currency_id',
            'valid_sales_account',
            'valid_purchases_account',
        )

    def validate_description(self, description: Optional[str]) -> Optional[str]:
        """
        description: A description of the transactions that will be recorded in the Global Nominal Account
        type: string
        """
        if description is None:
            description = ''
        description = str(description).strip()
        if len(description) == 0:
            return 'financial_global_nominal_account_create_101'
        if len(str(description)) > self.get_field('description').max_length:
            return 'financial_global_nominal_account_create_102'
        account = GlobalNominalAccount.objects.filter(
            description__iexact=description,
            member_id=self.request.user.member['id'],
        )
        if account.exists():
            return 'financial_global_nominal_account_create_103'
        self.cleaned_data['description'] = description
        return None

    def validate_nominal_account_type_id(self, nominal_account_type_id: Optional[int]) -> Optional[str]:
        """
        description: The id of a Nominal Account Type that the Nominal Account will belong to
        type: integer
        """
        try:
            nominal_account_type = NominalAccountType.objects.get(
                id=int(cast(int, nominal_account_type_id)),
            )
        except (ValueError, TypeError):
            return 'financial_global_nominal_account_create_104'
        except NominalAccountType.DoesNotExist:
            return 'financial_global_nominal_account_create_105'
        self.cleaned_data['nominal_account_type'] = nominal_account_type
        return None

    def validate_nominal_account_number(self, nominal_account_number: Optional[int]) -> Optional[str]:
        """
        description: The Number given to the Nominal Account that's unique within the Member
        type: integer
        """
        try:
            nominal_account_number = int(cast(int, nominal_account_number))
        except (ValueError, TypeError):
            return 'financial_global_nominal_account_create_106'
        account_type = self.cleaned_data.get('nominal_account_type', False)
        if not account_type:
            return None
        if nominal_account_number > account_type.max_account_number \
                or nominal_account_number < account_type.min_account_number:
            return 'financial_global_nominal_account_create_107'
        account = GlobalNominalAccount.objects.filter(
            nominal_account_number=nominal_account_number,
            member_id=self.request.user.member['id'],
        )
        if account.exists():
            return 'financial_global_nominal_account_create_108'
        self.cleaned_data['nominal_account_number'] = nominal_account_number
        return None

    def validate_external_reference(self, external_reference: Optional[str]) -> Optional[str]:
        """
        description: A reference to previous Account Numbers for Users migrating from different accounting systems
        type: string
        """
        if not external_reference:
            return None
        if len(str(external_reference)) > self.get_field('external_reference').max_length:
            return 'financial_global_nominal_account_create_109'
        account = GlobalNominalAccount.objects.filter(
            external_reference__iexact=external_reference,
            member_id=self.request.user.member['id'],
        )
        if account.exists():
            return 'financial_global_nominal_account_create_110'
        self.cleaned_data['external_reference'] = external_reference
        return None

    def validate_currency_id(self, currency_id: Optional[int]) -> Optional[str]:
        """
        description: The id of the Currency used for the account
        type: integer
        """
        try:
            currency_id = int(cast(int, currency_id))
        except(ValueError, TypeError):
            return 'financial_global_nominal_account_create_111'
        response = Membership.currency.read(
            token=self.request.user.token,
            pk=currency_id,
            span=self.span,
        )
        if response.status_code != 200:
            return 'financial_global_nominal_account_create_112'
        self.cleaned_data['currency_id'] = currency_id
        return None

    def validate_valid_sales_account(self, valid_sales_account: Optional[bool]) -> Optional[str]:
        """
        description: Flag for whether this Account can be used to store sales transactions
        type: boolean
        """
        try:
            nominal_account_type = self.cleaned_data['nominal_account_type']
        except KeyError:
            return None
        if nominal_account_type.min_account_number == SALES_ACCOUNT:
            valid = True
        elif nominal_account_type.min_account_number == PURCHASES_ACCOUNT:
            valid = False
        elif nominal_account_type.min_account_number in \
                [FIXED_ASSETS_ACCOUNT, OVERHEADS_ACCOUNT, DIRECT_EXPENSES_ACCOUNT]:
            if valid_sales_account is None or not isinstance(valid_sales_account, bool):
                return 'financial_global_nominal_account_create_113'
            valid = valid_sales_account
        else:
            valid = False
        self.cleaned_data['valid_sales_account'] = valid
        return None

    def validate_valid_purchases_account(self, valid_purchases_account: Optional[bool]) -> Optional[str]:
        """
        description: Flag for whether this Account can be used to store purchases transactions
        type: boolean
        """
        try:
            nominal_account_type = self.cleaned_data['nominal_account_type']
        except KeyError:
            return None
        if nominal_account_type.min_account_number == SALES_ACCOUNT:
            valid = False
        elif nominal_account_type.min_account_number == PURCHASES_ACCOUNT:
            valid = True
        elif nominal_account_type.min_account_number in \
                [FIXED_ASSETS_ACCOUNT, OVERHEADS_ACCOUNT, DIRECT_EXPENSES_ACCOUNT]:
            if valid_purchases_account is None or not isinstance(valid_purchases_account, bool):
                return 'financial_global_nominal_account_create_114'
            valid = valid_purchases_account
        else:
            valid = False
        self.cleaned_data['valid_purchases_account'] = valid
        return None


class GlobalNominalAccountUpdateController(ControllerBase):
    """
    Validates User data used to update a Global/Address Nominal Account record
    """

    class Meta:
        """
        Override some of the ControllerBase.Meta fields to make them more specific for this Controller
        """
        model = GlobalNominalAccount
        validation_order = (
            'address_id',
            'description',
            'external_reference',
            'currency_id',
            'valid_sales_account',
            'valid_purchases_account',
        )

    def validate_address_id(self, address_id: Optional[int]) -> Optional[str]:
        """
        description: The id of the Address whose account will be updated
        type: integer
        """
        if not address_id:
            return None
        try:
            address_id = int(cast(int, address_id))
        except (TypeError, ValueError):
            return 'financial_global_nominal_account_update_101'
        self.cleaned_data['address_id'] = address_id
        return None

    def validate_description(self, description: Optional[str]) -> Optional[str]:
        """
        description: A description of the transactions that will be recorded in the Global Nominal Account
        type: string
        """
        if description is None:
            description = ''
        description = str(description).strip()
        if len(description) == 0:
            return 'financial_global_nominal_account_update_102'
        if len(description) > self.get_field('description').max_length:
            return 'financial_global_nominal_account_update_103'
        if 'address_id' in self._errors:
            # The User tried to update an Address Account but the Address id was invalid. There's no point continuing
            return None
        # Check if the update is for Global or Address Accounts. Make sure the description is unique
        if 'address_id' in self.cleaned_data:
            account = AddressNominalAccount.objects.filter(
                address_id=self.cleaned_data['address_id'],
                description=description,
            ).exclude(global_nominal_account_id=self._instance.pk)
            if account.exists():
                return 'financial_global_nominal_account_update_104'
        else:
            # No Address was sent, User was updating a Global Nominal Account
            account = GlobalNominalAccount.objects.filter(
                member_id=self.request.user.member['id'],
                description=description,
            ).exclude(pk=self._instance.pk)
            if account.exists():
                return 'financial_global_nominal_account_update_105'
        self.cleaned_data['description'] = description
        return None

    def validate_external_reference(self, external_reference: Optional[str]) -> Optional[str]:
        """
        description: A reference to previous Account Numbers for Users migrating from different accounting systems
        type: string
        """
        if not external_reference:
            return None
        # The User is updating the Address Account only or tried to update an Address Account and an error occured.
        if 'address_id' in self.cleaned_data or 'address_id' in self._errors:
            return None
        if len(str(external_reference)) > self.get_field('external_reference').max_length:
            return 'financial_global_nominal_account_update_106'
        # Make sure the external reference is unique within the Member
        account = GlobalNominalAccount.objects.filter(
            external_reference__iexact=external_reference,
            member_id=self.request.user.member['id'],
        ).exclude(pk=self._instance.pk)
        if account.exists():
            return 'financial_global_nominal_account_update_107'
        self.cleaned_data['external_reference'] = external_reference
        return None

    def validate_currency_id(self, currency_id: Optional[int]) -> Optional[str]:
        """
        description: The id of the Currency used for the account
        type: integer
        """
        try:
            currency_id = int(cast(int, currency_id))
        except(ValueError, TypeError):
            return 'financial_global_nominal_account_update_108'
        response = Membership.currency.read(
            token=self.request.user.token,
            pk=currency_id,
            span=self.span,
        )
        if response.status_code != 200:
            return 'financial_global_nominal_account_update_109'
        self.cleaned_data['currency_id'] = currency_id
        return None

    def validate_valid_sales_account(self, valid_sales_account: Optional[bool]) -> Optional[str]:
        """
        description: Flag for whether this Account can be used to store sales transactions
        type: boolean
        """
        # The User is updating the Address Account only or tried to update an Address Account and an error occured.
        if 'address_id' in self.cleaned_data or 'address_id' in self._errors:
            return None
        nominal_account_type_number = self._instance.nominal_account_type.min_account_number
        if nominal_account_type_number == SALES_ACCOUNT:
            valid = True
        elif nominal_account_type_number == PURCHASES_ACCOUNT:
            valid = False
        elif nominal_account_type_number in [FIXED_ASSETS_ACCOUNT, OVERHEADS_ACCOUNT, DIRECT_EXPENSES_ACCOUNT]:
            if valid_sales_account is None or not isinstance(valid_sales_account, bool):
                return 'financial_global_nominal_account_update_110'
            valid = valid_sales_account
        else:
            valid = False
        self.cleaned_data['valid_sales_account'] = valid
        return None

    def validate_valid_purchases_account(self, valid_purchases_account: Optional[bool]) -> Optional[str]:
        """
        description: Flag for whether this Account can be used to store purchases transactions
        type: boolean
        """
        # The User is updating the Address Account only or tried to update an Address Account and an error occured.
        if 'address_id' in self.cleaned_data or 'address_id' in self._errors:
            return None
        nominal_account_type_number = self._instance.nominal_account_type.min_account_number
        if nominal_account_type_number == SALES_ACCOUNT:
            valid = False
        elif nominal_account_type_number == PURCHASES_ACCOUNT:
            valid = True
        elif nominal_account_type_number in [FIXED_ASSETS_ACCOUNT, OVERHEADS_ACCOUNT, DIRECT_EXPENSES_ACCOUNT]:
            if valid_purchases_account is None or not isinstance(valid_purchases_account, bool):
                return 'financial_global_nominal_account_update_111'
            valid = valid_purchases_account
        else:
            valid = False
        self.cleaned_data['valid_purchases_account'] = valid
        return None
