# stdlib
from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import cast, Dict, Optional, Union
# libs
from cloudcix.api.membership import Membership
from cloudcix.api.reporting import Reporting
from cloudcix_rest.controllers import ControllerBase
# local
from financial.models import AddressNominalAccount, NominalContra, NominalLedger, PaymentMethod


__all__ = [
    'AccountPurchasePaymentCreateController',
    'AccountPurchasePaymentContraCreateController',
]

DEBIT = Dict[str, Union[int, str, Decimal]]
PAYMENT_ACCOUNT_RANGE = range(1000, 3000)


class AccountPurchasePaymentCreateController(ControllerBase):
    """
    Validate User data to create a new Nominal Ledger record for an Account Purchase Payment transaction
    """

    class Meta(ControllerBase.Meta):
        """
        Override some of the ControllerBase.Meta fields to make them more specific for this Controller
        """
        model = NominalLedger
        validation_order = (
            'amount',
            'contra_address_id',
            'narrative',
            'payment_method_id',
            'report_template_id',
            'transaction_date',
            'exchange_rate',
        )

    def validate_amount(self, amount: Optional[str]) -> Optional[str]:
        """
        description: The amount of money being paid
        type: string
        format: decimal
        """
        try:
            decimal_amount = Decimal(str(amount))
        except (InvalidOperation, KeyError):
            return 'financial_account_purchase_payment_create_101'
        if decimal_amount < Decimal('0'):
            return 'financial_account_purchase_payment_create_102'
        self.cleaned_data['amount'] = decimal_amount.quantize(Decimal('1.00'))
        return None

    def validate_contra_address_id(self, contra_address_id: Optional[int]) -> Optional[str]:
        """
        description: The id of the Address who the requesting User is paying
        type: integer
        """
        try:
            contra_address_id = int(cast(int, contra_address_id))
        except (TypeError, ValueError):
            return 'financial_account_purchase_payment_create_103'
        response = Membership.address.read(
            token=self.request.user.token,
            pk=contra_address_id,
            span=self.span,
        )
        if response.status_code != 200:
            return 'financial_account_purchase_payment_create_104'
        self.cleaned_data['contra_address_id'] = contra_address_id
        self.cleaned_data['contra_address'] = response.json()['content']
        return None

    def validate_narrative(self, narrative: Optional[str]) -> Optional[str]:
        """
        description: A summary of the Purchase Payment
        type: string
        """
        if narrative is None:
            narrative = ''
        narrative = str(narrative).strip()
        if len(narrative) > self.get_field('narrative').max_length:
            return 'financial_account_purchase_payment_create_105'
        self.cleaned_data['narrative'] = narrative
        return None

    def validate_payment_method_id(self, payment_method_id: Optional[int]) -> Optional[str]:
        """
        description: How the requesting User intends to pay the amount of the transaction
        type: integer
        """
        try:
            PaymentMethod.objects.get(
                id=int(cast(int, payment_method_id)),
                member_id=self.request.user.member['id'],
            )
        except (TypeError, ValueError):
            return 'financial_account_purchase_payment_create_106'
        except PaymentMethod.DoesNotExist:
            return 'financial_account_purchase_payment_create_107'

        try:
            # Find the Nominal Account that will be credited
            contra = NominalContra.objects.get(
                payment_method_id=payment_method_id,
                transaction_type_id=10004,
            )
        except NominalContra.DoesNotExist:
            return 'financial_account_purchase_payment_create_108'

        if contra.global_nominal_account.nominal_account_number not in PAYMENT_ACCOUNT_RANGE:
            return 'financial_account_purchase_payment_create_109'

        # Lastly, make sure the User has an Address Nominal Account set up for this Global Nominal Account
        try:
            AddressNominalAccount.objects.get(
                address_id=self.request.user.address['id'],
                global_nominal_account_id=contra.global_nominal_account_id,
            )
        except AddressNominalAccount.DoesNotExist:
            return 'financial_account_purchase_payment_create_110'

        self.cleaned_data['nominal_account_number'] = contra.global_nominal_account.nominal_account_number
        return None

    def validate_report_template_id(self, report_template_id: Optional[int]) -> Optional[str]:
        """
        description: The id of the Report Template to use when printing the Purchase Payment
        type: integer
        """
        if report_template_id is None:
            return None
        try:
            report_template_id = int(cast(int, report_template_id))
        except (TypeError, ValueError):
            return 'financial_account_purchase_payment_create_111'
        response = Reporting.report_template.read(
            token=self.request.user.token,
            pk=report_template_id,
            span=self.span,
        )
        if response.status_code != 200:
            return 'financial_account_purchase_payment_create_112'
        if response.json()['content']['idTransactionType'] != 10004:
            return 'financial_account_purchase_payment_create_113'
        self.cleaned_data['report_template_id'] = report_template_id
        return None

    def validate_transaction_date(self, date: Optional[str]) -> Optional[str]:
        """
        description: The date that the Payment was made
        type: string
        """
        try:
            transaction_date = datetime.strptime(str(date).split('T')[0], '%Y-%m-%d').date()
        except (TypeError, ValueError):
            return 'financial_account_purchase_payment_create_114'
        obj = NominalLedger.period_end.filter(
            address_id=self.request.user.address['id'],
            transaction_date__gte=transaction_date,
        )
        if obj.exists():
            return 'financial_account_purchase_payment_create_115'
        self.cleaned_data['transaction_date'] = transaction_date
        return None

    def validate_exchange_rate(self, exchange_rate: Optional[str]) -> Optional[str]:
        """
        description: The exchange rate between the currency of the User's Address and of the Contra Account
        type: string
        format: Decimal
        """
        # Find out if an exchange rate is required. First find out if the contra account is in a different currency to
        # the requesting User's Address
        account_number = self.cleaned_data.get('nominal_account_number')
        if account_number is None:
            return None

        currency_id = AddressNominalAccount.objects.values_list('currency_id', flat=True).get(
            address_id=self.request.user.address['id'],
            global_nominal_account__nominal_account_number=account_number,
        )
        if currency_id == self.request.user.address['currency_id']:
            return None

        # The Contra Account and the currency of the Address are different. Validate the exchange rate
        try:
            self.cleaned_data['exchange_rate'] = Decimal(str(exchange_rate))
        except InvalidOperation:
            return 'financial_account_purchase_payment_create_116'

        return None


class AccountPurchasePaymentContraCreateController(ControllerBase):
    """
    Validate User data to create a new Nominal Ledger record for an Account Purchase Payment transaction
    """

    class Meta(ControllerBase.Meta):
        """
        Override some of the ControllerBase.Meta fields to make them more specific for this Controller
        """
        model = NominalLedger
        validation_order = (
            'narrative',
            'report_template_id',
            'transaction_date',
            'tsn',
            'payment_method_id',
            'exchange_rate',
        )

    def validate_narrative(self, narrative: Optional[str]) -> Optional[str]:
        """
        description: A summary of the Purchase Payment
        type: string
        """
        if narrative is None:
            narrative = ''
        narrative = str(narrative).strip()
        if len(narrative) > self.get_field('narrative').max_length:
            return 'financial_account_purchase_payment_contra_create_101'
        self.cleaned_data['narrative'] = narrative
        return None

    def validate_report_template_id(self, report_template_id: Optional[int]) -> Optional[str]:
        """
        description: The id of the Report Template to use when printing the Purchase Payment
        type: integer
        """
        if report_template_id is None:
            return None
        try:
            report_template_id = int(cast(int, report_template_id))
        except (TypeError, ValueError):
            return 'financial_account_purchase_payment_contra_create_102'
        response = Reporting.report_template.read(
            token=self.request.user.token,
            pk=report_template_id,
            span=self.span,
        )
        if response.status_code != 200:
            return 'financial_account_purchase_payment_contra_create_103'
        if response.json()['content']['idTransactionType'] != 10004:
            return 'financial_account_purchase_payment_contra_create_104'
        self.cleaned_data['report_template_id'] = report_template_id
        return None

    def validate_transaction_date(self, date: Optional[str]) -> Optional[str]:
        """
        description: The date that the Payment was made
        type: string
        """
        try:
            transaction_date = datetime.strptime(str(date).split('T')[0], '%Y-%m-%d').date()
        except (TypeError, ValueError):
            return 'financial_account_purchase_payment_contra_create_105'
        obj = NominalLedger.period_end.filter(
            address_id=self.request.user.address['id'],
            transaction_date__gte=transaction_date,
        )
        if obj.exists():
            return 'financial_account_purchase_payment_contra_create_106'
        self.cleaned_data['transaction_date'] = transaction_date
        return None

    def validate_tsn(self, tsn: Optional[int]) -> Optional[str]:
        """
        description: The Transaction Sequence Number of an Account Sale Payment in the specified Contra Address
        type: int
        """
        try:
            sale_payment = NominalLedger.account_sale_payments.get(
                tsn=int(cast(int, tsn)),
                address_id=self.address_id,
                contra_address_id=self.request.user.address['id'],
            )
        except (TypeError, ValueError):
            return 'financial_account_purchase_payment_contra_create_107'
        except NominalLedger.DoesNotExist:
            return 'financial_account_purchase_payment_contra_create_108'

        if sale_payment.contra_nominal_ledger is not None:
            return 'financial_account_purchase_payment_contra_create_109'

        self.cleaned_data['contra_nominal_ledger'] = sale_payment
        return None

    def validate_payment_method_id(self, payment_method_id: Optional[int]) -> Optional[str]:
        """
        description: How the requesting User intends to pay the amount on the transaction
        type: integer
        """
        try:
            PaymentMethod.objects.get(
                id=int(cast(int, payment_method_id)),
                member_id=self.request.user.member['id'],
            )
        except (TypeError, ValueError):
            return 'financial_account_purchase_payment_contra_create_110'
        except PaymentMethod.DoesNotExist:
            return 'financial_account_purchase_payment_contra_create_111'

        try:
            # Find the Nominal Account that will be credited
            nominal_account_id = NominalContra.objects.values_list('global_nominal_account_id', flat=True).get(
                payment_method_id=payment_method_id,
                transaction_type_id=10004,
            )
        except NominalContra.DoesNotExist:
            return 'financial_account_purchase_payment_contra_create_112'

        # Make sure the User has an Address Nominal Account set up for this Global Nominal Account
        try:
            address_account = AddressNominalAccount.objects.get(
                address_id=self.request.user.address['id'],
                global_nominal_account_id=nominal_account_id,
            )
        except AddressNominalAccount.DoesNotExist:
            return 'financial_account_purchase_payment_contra_create_113'

        if address_account.global_nominal_account.nominal_account_number not in PAYMENT_ACCOUNT_RANGE:
            return 'financial_account_purchase_payment_contra_create_114'

        # Lastly, check that the currency ids of this Account and the Account from the contra transaction match
        sale_payment = self.cleaned_data.get('contra_nominal_ledger')
        if sale_payment is None:
            return None
        # Get the currency of the Nominal Account that was used on the Sale Payment
        account_number = sale_payment.debits.first().nominal_account_number
        transaction_currency_id = AddressNominalAccount.objects.values_list('currency_id', flat=True).get(
            address_id=sale_payment.address_id,
            global_nominal_account__nominal_account_number=account_number,
        )
        if address_account.currency_id != transaction_currency_id:
            return 'financial_account_purchase_payment_contra_create_115'

        self.cleaned_data['nominal_account_number'] = address_account.global_nominal_account.nominal_account_number
        return None

    def validate_exchange_rate(self, exchange_rate: Optional[str]) -> Optional[str]:
        """
        description: The exchange rate between the currency of the User's Address and of the Contra Account
        type: string
        format: decimal
        """
        # Find out if an exchange rate is required. First find out if the contra account is in a different currency to
        # the requesting User's Address
        account_number = self.cleaned_data.get('nominal_account_number')
        if account_number is None:
            return None

        currency_id = AddressNominalAccount.objects.values_list('currency_id', flat=True).get(
            address_id=self.request.user.address['id'],
            global_nominal_account__nominal_account_number=account_number,
        )
        if currency_id == self.request.user.address['currency_id']:
            return None

        # The Contra Account and the currency of the Address are different. Validate the exchange rate
        try:
            self.cleaned_data['exchange_rate'] = Decimal(str(exchange_rate))
        except InvalidOperation:
            return 'financial_account_purchase_payment_contra_create_116'

        return None
