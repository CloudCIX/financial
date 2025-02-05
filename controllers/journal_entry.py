# stdlib
from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import cast, Dict, List, Optional, Union
# libs
from cloudcix.api.reporting import Reporting
from cloudcix_rest.controllers import ControllerBase
# local
from financial import reserved_accounts as reserved
from financial.models.address_nominal_account import AddressNominalAccount
from financial.models.nominal_ledger import NominalLedger


__all__ = [
    'JournalEntryListController',
    'JournalEntryCreateController',
    'JournalEntryUpdateController',
]

DEBITS = Dict[str, Union[int, str, Decimal]]
CREDITS = DEBITS
INVALID_NUMBERS = [reserved.CREDITOR_CONTROL_ACCOUNT, reserved.DEBTOR_CONTROL_ACCOUNT]


class JournalEntryListController(ControllerBase):
    """
    Validates User data used to filter a list of Nominal Ledger records for Journal Entry transactions
    """

    class Meta(ControllerBase.Meta):
        """
        Override some of the ControllerBase.Meta fields to make them more specific for this controller
        """
        allowed_ordering = (
            'narrative',
            'transaction_date',
            'tsn',
        )
        search_fields = {
            'created': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
            'transaction_date': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
            'tsn': ControllerBase.DEFAULT_NUMBER_FILTER_OPERATORS,
        }


class JournalEntryCreateController(ControllerBase):
    """
    Validates User data used to create a new Nominal Ledger record for Journal Entry transactions
    """

    class Meta(ControllerBase.Meta):
        """
        Override some of the ControllerBase.Meta fields to make them more specific for this controller
        """
        model = NominalLedger
        validation_order = (
            'credits',
            'debits',
            'narrative',
            'report_template_id',
            'transaction_date',
        )

    def validate_credits(self, credits: Optional[List[CREDITS]]) -> Optional[str]:
        """
        description: The amounts to credit from Nominal Accounts in the User's Address
        type: array
        items:
            type: object
            properties:
                amount:
                    type: string
                    format: decimal
                number:
                    type: integer
        """
        if credits is None:
            return 'financial_journal_entry_create_101'

        account_numbers: List[int] = list()
        for credit in credits:
            try:
                credit['amount'] = Decimal(str(credit['amount'])).quantize(Decimal('1.0000'))
            except (KeyError, InvalidOperation):
                return 'financial_journal_entry_create_102'
            if credit['amount'] == 0:
                return 'financial_journal_entry_create_103'

            try:
                account_number = int(cast(int, credit['number']))
            except (KeyError, TypeError, ValueError):
                return 'financial_journal_entry_create_104'
            if account_number in account_numbers:
                return 'financial_journal_entry_create_105'
            if account_number in INVALID_NUMBERS:
                return 'financial_journal_entry_create_106'
            account_numbers.append(account_number)
            credit['number'] = account_number

        # Make sure all the Nominal Accounts exist
        accounts = AddressNominalAccount.objects.filter(
            address_id=self.request.user.address['id'],
            global_nominal_account__nominal_account_number__in=account_numbers,
        )
        if len(account_numbers) != accounts.count():
            return 'financial_journal_entry_create_107'

        self.cleaned_data['credits'] = credits
        return None

    def validate_debits(self, debits: Optional[List[DEBITS]]) -> Optional[str]:
        """
        description: The amounts to debit to Nominal Accounts in the User's Address
        type: array
        items:
            type: object
            properties:
                amount:
                    type: string
                    format: decimal
                number:
                    type: integer
        """
        if debits is None:
            return 'financial_journal_entry_create_108'

        account_numbers: List[int] = list()
        for debit in debits:
            try:
                debit['amount'] = Decimal(str(debit['amount'])).quantize(Decimal('1.0000'))
            except (KeyError, InvalidOperation):
                return 'financial_journal_entry_create_109'
            if debit['amount'] == 0:
                return 'financial_journal_entry_create_110'

            try:
                account_number = int(cast(int, debit['number']))
            except (KeyError, TypeError, ValueError):
                return 'financial_journal_entry_create_111'
            if account_number in account_numbers:
                return 'financial_journal_entry_create_112'
            if account_number in INVALID_NUMBERS:
                return 'financial_journal_entry_create_113'
            account_numbers.append(account_number)
            debit['number'] = account_number

        # Make sure all the Nominal Accounts exists
        accounts = AddressNominalAccount.objects.filter(
            address_id=self.request.user.address['id'],
            global_nominal_account__nominal_account_number__in=account_numbers,
        )
        if len(account_numbers) != accounts.count():
            return 'financial_journal_entry_create_114'

        # Make sure the debit and credit amounts match and that no Nominal Account Numbers are repeated
        if 'credits' not in self.cleaned_data:
            return None

        credit_amount = Decimal('0')
        for c in self.cleaned_data['credits']:
            if c['number'] in account_numbers:
                return 'financial_journal_entry_create_115'
            credit_amount += c['amount']

        debit_amount = sum([d['amount'] for d in debits])
        if credit_amount != debit_amount:
            return 'financial_journal_entry_create_116'

        self.cleaned_data['debits'] = debits
        return None

    def validate_narrative(self, narrative: str) -> Optional[str]:
        """
        description: Short description of why the Journal Entry was made
        type: string
        """
        if narrative is None:
            narrative = ''
        narrative = str(narrative).strip()
        if len(narrative) > self.get_field('narrative').max_length:
            return 'financial_journal_entry_create_117'
        self.cleaned_data['narrative'] = narrative
        return None

    def validate_report_template_id(self, report_template_id: Optional[int]) -> Optional[str]:
        """
        description: The id of the Report Template to use when printing the Journal Entry
        type: integer
        """
        if report_template_id is None:
            return None
        try:
            report_template_id = int(cast(int, report_template_id))
        except (TypeError, ValueError):
            return 'financial_journal_entry_create_118'
        response = Reporting.report_template.read(
            token=self.request.user.token,
            pk=report_template_id,
            span=self.span,
        )
        if response.status_code != 200:
            return 'financial_journal_entry_create_119'
        if response.json()['content']['idTransactionType'] != 12000:
            return 'financial_journal_entry_create_120'
        self.cleaned_data['report_template_id'] = report_template_id
        return None

    def validate_transaction_date(self, date: Optional[str]) -> Optional[str]:
        """
        description: The date that the Journal Entry was issued
        type: string
        """
        try:
            transaction_date = datetime.strptime(str(date).split('T')[0], '%Y-%m-%d')
        except (TypeError, ValueError):
            return 'financial_journal_entry_create_121'

        # Make sure the new transaction date is not processed by a period end
        period_end = NominalLedger.period_end.filter(
            address_id=self.request.user.address['id'],
            transaction_date__gte=transaction_date,
        )
        if period_end.exists():
            return 'financial_journal_entry_create_122'

        self.cleaned_data['transaction_date'] = transaction_date
        return None


class JournalEntryUpdateController(ControllerBase):
    """
    Validates User data used to update a Nominal Ledger record for Journal Entry transactions
    """

    class Meta(ControllerBase.Meta):
        """
        Override some of the ControllerBase.Meta fields to make them more specific for this controller
        """
        model = NominalLedger
        validation_order = (
            'narrative',
            'report_template_id',
            'transaction_date',
        )

    def validate_narrative(self, narrative: Optional[str]) -> Optional[str]:
        """
        description: A short description of why the Journal Entry was made
        type: string
        """
        if narrative is None:
            narrative = ''
        narrative = str(narrative).strip()
        if len(narrative) > self.get_field('narrative').max_length:
            return 'financial_journal_entry_update_101'
        self.cleaned_data['narrative'] = narrative
        return None

    def validate_report_template_id(self, report_template_id: Optional[int]) -> Optional[str]:
        """
        description: The id of the Report Template to use when printing the Journal Entry
        type: integer
        """
        if report_template_id is None:
            return None
        try:
            report_template_id = int(cast(int, report_template_id))
        except (TypeError, ValueError):
            return 'financial_journal_entry_update_102'
        response = Reporting.report_template.read(
            token=self.request.user.token,
            pk=report_template_id,
            span=self.span,
        )
        if response.status_code != 200:
            return 'financial_journal_entry_update_103'
        if response.json()['content']['idTransactionType'] != 12000:
            return 'financial_journal_entry_update_104'
        self.cleaned_data['report_template_id'] = report_template_id
        return None

    def validate_transaction_date(self, date: Optional[str]) -> Optional[str]:
        """
        description: The date that the Journal Entry was issued
        type: string
        """
        try:
            transaction_date = datetime.strptime(str(date).split('T')[0], '%Y-%m-%d')
        except (TypeError, ValueError):
            return 'financial_journal_entry_update_105'

        # Make sure the new transaction date is not processed by a period end
        period_end = NominalLedger.period_end.filter(
            address_id=self.request.user.address['id'],
            transaction_date__gte=transaction_date,
        )
        if period_end.exists():
            return 'financial_journal_entry_update_106'

        self.cleaned_data['transaction_date'] = transaction_date
        return None
