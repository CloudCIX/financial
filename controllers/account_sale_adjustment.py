# stdlib
from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import cast, Dict, Optional
# libs
from cloudcix.api.membership import Membership
from cloudcix.api.reporting import Reporting
from cloudcix_rest.controllers import ControllerBase
# local
from financial.models.address_nominal_account import AddressNominalAccount
from financial.models.nominal_ledger import NominalLedger
from financial import reserved_accounts as reserved


__all__ = [
    'AccountSaleAdjustmentCreateController',
    'AccountSaleAdjustmentContraCreateController',
]

DEBIT = Dict[str, int]
CREDIT = DEBIT


class AccountSaleAdjustmentCreateController(ControllerBase):
    """
    Validate User data to create a new Nominal Ledger record for an Account Sale Adjustment transaction
    """

    class Meta(ControllerBase.Meta):
        """
        Override some of the ControllerBase.Meta fields to make them more specific for this Controller
        """
        model = NominalLedger
        validation_order = (
            'contra_address_id',
            'narrative',
            'report_template_id',
            'transaction_date',
            'debit',
            'credit',
        )

    def validate_contra_address_id(self, contra_address_id: Optional[int]) -> Optional[str]:
        """
        description: The id of the Address that the Account Sale Adjustment will be made for
        type: integer
        """
        try:
            contra_address_id = int(cast(int, contra_address_id))
        except (ValueError, TypeError):
            return 'financial_account_sale_adjustment_create_101'
        response = Membership.address.read(
            token=self.request.user.token,
            pk=contra_address_id,
            span=self.span,
        )
        if response.status_code != 200:
            return 'financial_account_sale_adjustment_create_102'
        self.cleaned_data['contra_address'] = response.json()['content']
        self.cleaned_data['contra_address_id'] = contra_address_id
        return None

    def validate_narrative(self, narrative: Optional[str]) -> Optional[str]:
        """
        description: Short explanation of the details of the Account Sale Adjustment
        type: string
        """
        if narrative is None:
            narrative = ''
        narrative = str(narrative).strip()
        if len(narrative) > self.get_field('narrative').max_length:
            return 'financial_account_sale_adjustment_create_103'
        self.cleaned_data['narrative'] = narrative
        return None

    def validate_report_template_id(self, report_template_id: Optional[int]) -> Optional[str]:
        """
        description: The id of the Report Template to use when printing the Account Sale Adjustment
        type: integer
        """
        if not report_template_id:
            return None
        try:
            report_template_id = int(cast(int, report_template_id))
        except (ValueError, TypeError):
            return 'financial_account_sale_adjustment_create_104'
        response = Reporting.report_template.read(
            token=self.request.user.token,
            pk=report_template_id,
        )
        if response.status_code != 200:
            return 'financial_account_sale_adjustment_create_105'
        if response.json()['content']['idTransactionType'] != 11005:
            return 'financial_account_sale_adjustment_create_106'
        self.cleaned_data['report_template_id'] = report_template_id
        return None

    def validate_transaction_date(self, transaction: Optional[str]) -> Optional[str]:
        """
        description: The date that the Transaction was made
        type: string
        """
        try:
            transaction_date = datetime.strptime(str(transaction).split('T')[0], '%Y-%m-%d').date()
        except (TypeError, ValueError):
            return 'financial_account_sale_adjustment_create_107'
        # Make sure the date has not been processed by a period end
        obj = NominalLedger.period_end.filter(
            address_id=self.request.user.address['id'],
            transaction_date__gte=transaction_date,
        )
        if obj.exists():
            return 'financial_account_sale_adjustment_create_108'
        self.cleaned_data['transaction_date'] = transaction_date
        return None

    def validate_debit(self, debit: Optional[DEBIT]) -> Optional[str]:
        """
        description: |
            A dictionary of the `amount` to debit to a Nominal Account with a given `number` in the User's Address
        type: object
        properties:
            amount:
                type: string
                format: decimal
            number:
                type: integer
        """
        if not isinstance(debit, dict):
            return 'financial_account_sale_adjustment_create_109'

        try:
            # Convert debit amount to a Decimal, then round to 2 decimal places
            decimal_amount = Decimal(str(debit['amount']))
            decimal_amount = decimal_amount.quantize(Decimal('1.00'))
        except (KeyError, InvalidOperation):
            return 'financial_account_sale_adjustment_create_110'
        if decimal_amount == Decimal('0'):
            return 'financial_account_sale_adjustment_create_111'

        try:
            number = int(cast(int, debit['number']))
        except (TypeError, ValueError, KeyError):
            return 'financial_account_sale_adjustment_create_112'

        if number == reserved.CREDITOR_CONTROL_ACCOUNT:
            return 'financial_account_sale_adjustment_create_113'

        if number == reserved.DEBTOR_CONTROL_ACCOUNT:
            self.cleaned_data['unallocated_balance'] = decimal_amount
        else:
            obj = AddressNominalAccount.objects.filter(
                address_id=self.request.user.address['id'],
                global_nominal_account__nominal_account_number=number,
            )
            if not obj.exists():
                return 'financial_account_sale_adjustment_create_114'

        self.cleaned_data['debit'] = {'amount': decimal_amount, 'number': number}
        return None

    def validate_credit(self, credit: Optional[CREDIT]) -> Optional[str]:
        """
        description: |
            A dictionary of the `amount` to credit from a Nominal Account with a given `number` in the User's Address
        type: object
        properties:
            amount:
                type: string
                format: decimal
            number:
                type: integer
        """
        if not isinstance(credit, dict):
            return 'financial_account_sale_adjustment_create_115'

        try:
            # Convert credit amount to a Decimal, then round to 2 decimal places
            decimal_amount = Decimal(str(credit['amount']))
            decimal_amount = decimal_amount.quantize(Decimal('1.00'))
        except (KeyError, InvalidOperation):
            return 'financial_account_sale_adjustment_create_116'
        if decimal_amount == Decimal('0'):
            return 'financial_account_sale_adjustment_create_117'

        try:
            number = int(cast(int, credit['number']))
        except (TypeError, ValueError, KeyError):
            return 'financial_account_sale_adjustment_create_118'

        if number == reserved.CREDITOR_CONTROL_ACCOUNT:
            return 'financial_account_sale_adjustment_create_119'

        if number == reserved.DEBTOR_CONTROL_ACCOUNT:
            self.cleaned_data['unallocated_balance'] = decimal_amount * -1
        else:
            obj = AddressNominalAccount.objects.filter(
                address_id=self.request.user.address['id'],
                global_nominal_account__nominal_account_number=number,
            )
            if not obj.exists():
                return 'financial_account_sale_adjustment_create_120'

        # For the last bit of validation, we need to make sure the debit and credit are valid together, so exit if
        # there was a problem with the debit
        debit = self.cleaned_data.get('debit')
        if debit is None:
            return None

        # Make sure the debtor control account is used exactly once
        if number == debit['number']:
            return 'financial_account_sale_adjustment_create_121'
        if reserved.DEBTOR_CONTROL_ACCOUNT not in (number, debit['number']):
            return 'financial_account_sale_adjustment_create_122'

        # Make sure the debit and credit amounts match
        if decimal_amount != self.cleaned_data['debit']['amount']:
            return 'financial_account_sale_adjustment_create_123'

        self.cleaned_data['credit'] = {'amount': decimal_amount, 'number': number}
        return None


class AccountSaleAdjustmentContraCreateController(ControllerBase):
    """
    Validate User data to create a new Nominal Ledger record for an Account Sale Adjustment transaction
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
            'debit',
            'credit',
        )

    def validate_narrative(self, narrative: Optional[str]) -> Optional[str]:
        """
        description: Short explanation of the details of the Account Sale Adjustment
        type: string
        """
        if narrative is None:
            narrative = ''
        narrative = str(narrative).strip()
        if len(narrative) > self.get_field('narrative').max_length:
            return 'financial_account_sale_adjustment_contra_create_101'
        self.cleaned_data['narrative'] = narrative
        return None

    def validate_report_template_id(self, report_template_id: Optional[int]) -> Optional[str]:
        """
        description: The id of the Report Template to use when printing the Account Sale Adjustment
        type: integer
        """
        if not report_template_id:
            return None
        try:
            report_template_id = int(cast(int, report_template_id))
        except (ValueError, TypeError):
            return 'financial_account_sale_adjustment_contra_create_102'
        response = Reporting.report_template.read(
            token=self.request.user.token,
            pk=report_template_id,
        )
        if response.status_code != 200:
            return 'financial_account_sale_adjustment_contra_create_103'
        if response.json()['content']['idTransactionType'] != 11005:
            return 'financial_account_sale_adjustment_contra_create_104'
        self.cleaned_data['report_template_id'] = report_template_id
        return None

    def validate_transaction_date(self, transaction: Optional[str]) -> Optional[str]:
        """
        description: The date that the Transaction was made
        type: string
        """
        try:
            transaction_date = datetime.strptime(str(transaction).split('T')[0], '%Y-%m-%d').date()
        except (TypeError, ValueError):
            return 'financial_account_sale_adjustment_contra_create_105'
        # Make sure the date has not been processed by a period end
        obj = NominalLedger.period_end.filter(
            address_id=self.request.user.address['id'],
            transaction_date__gte=transaction_date,
        )
        if obj.exists():
            return 'financial_account_sale_adjustment_contra_create_106'
        self.cleaned_data['transaction_date'] = transaction_date
        return None

    def validate_tsn(self, tsn: Optional[int]) -> Optional[str]:
        """
        description: |
            The Transaction Sequence Number of an Account Purchase Adjustment from the Contra Address, from which a new
            Account Sale Adjustment will be made
        type: integer
        """
        try:
            tsn = int(cast(int, tsn))
        except (ValueError, TypeError):
            return 'financial_account_sale_adjustment_contra_create_107'

        try:
            # Fetch the Account Purchase Adjustment that the Account Sale Adjustment is being created in response to
            account_purchase_adjustment = NominalLedger.account_purchase_adjustments.get(
                tsn=tsn,
                address_id=self.address_id,
                contra_address_id=self.request.user.address['id'],
            )
        except NominalLedger.DoesNotExist:
            return 'financial_account_sale_adjustment_contra_create_108'
        if account_purchase_adjustment.contra_nominal_ledger is not None:
            return 'financial_account_sale_adjustment_contra_create_109'

        if 'transaction_date' not in self.cleaned_data:
            return None
        transaction_date = self.cleaned_data['transaction_date']
        if account_purchase_adjustment.transaction_date > transaction_date:
            return 'financial_account_sale_adjustment_contra_create_110'

        self.cleaned_data['contra_nominal_ledger'] = account_purchase_adjustment
        return None

    def validate_debit(self, debit: Optional[DEBIT]) -> Optional[str]:
        """
        description: |
            A dictionary of the `amount` to debit to a Nominal Account with a given `number` in the User's Address
        type: object
        properties:
            amount:
                type: string
                format: decimal
            number:
                type: integer
        """
        if not isinstance(debit, dict):
            return 'financial_account_sale_adjustment_contra_create_111'

        try:
            # Convert debit amount to a Decimal, then round to 2 decimal places
            decimal_amount = Decimal(str(debit['amount']))
            decimal_amount = decimal_amount.quantize(Decimal('1.00'))
        except (KeyError, InvalidOperation):
            return 'financial_account_sale_adjustment_contra_create_112'

        try:
            number = int(cast(int, debit['number']))
        except (TypeError, ValueError, KeyError):
            return 'financial_account_sale_adjustment_contra_create_113'

        # Now make sure the data is valid against the Account Purchase Adjustment
        if 'contra_nominal_ledger' not in self.cleaned_data:
            return None
        contra_credit = self.cleaned_data['contra_nominal_ledger'].credits.all()[0]

        if decimal_amount != contra_credit.amount:
            return 'financial_account_sale_adjustment_contra_create_114'

        # If the contra credit uses a control account, then so must this debit
        if contra_credit.nominal_account_number == reserved.CREDITOR_CONTROL_ACCOUNT:
            if number != reserved.DEBTOR_CONTROL_ACCOUNT:
                return 'financial_account_sale_adjustment_contra_create_115'
            self.cleaned_data['unallocated_balance'] = decimal_amount
        else:
            obj = AddressNominalAccount.objects.filter(
                address_id=self.request.user.address['id'],
                global_nominal_account__nominal_account_number=number,
            )
            if not obj.exists():
                return 'financial_account_sale_adjustment_contra_create_116'

        self.cleaned_data['debit'] = {'amount': decimal_amount, 'number': number}
        return None

    def validate_credit(self, credit: Optional[CREDIT]) -> Optional[str]:
        """
        description: |
            A dictionary of the `amount` to credit from a Nominal Account with a given `number` in the User's Address
        type: object
        properties:
            amount:
                type: string
                format: decimal
            number:
                type: integer
        """
        if not isinstance(credit, dict):
            return 'financial_account_sale_adjustment_contra_create_117'

        try:
            # Convert credit amount to a Decimal, then round to 2 decimal places
            decimal_amount = Decimal(str(credit['amount']))
            decimal_amount = decimal_amount.quantize(Decimal('1.00'))
        except (KeyError, InvalidOperation):
            return 'financial_account_sale_adjustment_contra_create_118'

        try:
            number = int(cast(int, credit['number']))
        except (TypeError, ValueError, KeyError):
            return 'financial_account_sale_adjustment_contra_create_119'

        # Now make sure the data is valid against the Account Purchase Adjustment
        if 'contra_nominal_ledger' not in self.cleaned_data:
            return None
        contra_debit = self.cleaned_data['contra_nominal_ledger'].debits.all()[0]

        if decimal_amount != contra_debit.amount:
            return 'financial_account_sale_adjustment_contra_create_120'

        # If the contra debit uses a control account, then so must this credit
        if contra_debit.nominal_account_number == reserved.CREDITOR_CONTROL_ACCOUNT:
            if number != reserved.DEBTOR_CONTROL_ACCOUNT:
                return 'financial_account_sale_adjustment_contra_create_121'
            self.cleaned_data['unallocated_balance'] = decimal_amount * -1
        else:
            obj = AddressNominalAccount.objects.filter(
                address_id=self.request.user.address['id'],
                global_nominal_account__nominal_account_number=number,
            )
            if not obj.exists():
                return 'financial_account_sale_adjustment_contra_create_122'

        self.cleaned_data['credit'] = {'amount': decimal_amount, 'number': number}
        return None
