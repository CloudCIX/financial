# stdlib
from collections import deque
from datetime import datetime
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from typing import cast, Deque, Dict, List, Optional, Set, Union
# libs
from cloudcix.api.membership import Membership
from cloudcix.api.reporting import Reporting
from cloudcix_rest.controllers import ControllerBase
# local
from financial import reserved_accounts as reserved
from financial.models.address_nominal_account import AddressNominalAccount
from financial.models.nominal_ledger import NominalLedger
from financial.models.nominal_ledger_debit import NominalLedgerDebit
from financial.models.tax_rate import TaxRate


__all__ = [
    'AccountSaleCreditNoteCreateController',
    'AccountSaleCreditNoteUpdateController',
    'AccountSaleCreditNoteContraCreateController',
]

DEBIT = Dict[str, Union[int, str, Decimal]]


class AccountSaleCreditNoteCreateController(ControllerBase):
    """
    Validate User data to create a new Nominal Ledger record for an Account Sale Credit Note transaction
    """

    class Meta(ControllerBase.Meta):
        """
        Override some of the ControllerBase.Meta fields to make them more specific for this Controller
        """
        model = NominalLedger
        validation_order = (
            'address1_deliver_to',
            'address2_deliver_to',
            'address3_deliver_to',
            'city_deliver_to',
            'contra_address_id',
            'contra_contact_id',
            'country_id_deliver_to',
            'external_reference',
            'name_deliver_to',
            'narrative',
            'lines',
            'postcode_deliver_to',
            'report_template_id',
            'subdivision_id_deliver_to',
            'transaction_date',
        )

    def validate_address1_deliver_to(self, address: Optional[str]) -> Optional[str]:
        """
        description: The first line of the geographic Address where the Sale Credit Note's items will be delivered to
        type: string
        """
        if address is None:
            address = ''
        address = str(address).strip()
        if len(address) == 0:
            return 'financial_account_sale_credit_note_create_101'
        if len(address) > self.get_field('address1_deliver_to').max_length:
            return 'financial_account_sale_credit_note_create_102'
        self.cleaned_data['address1_deliver_to'] = address
        return None

    def validate_address2_deliver_to(self, address: Optional[str]) -> Optional[str]:
        """
        description: The second line of the geographic Address where the Sale Credit Note's items will be delivered to
        type: string
        required: false
        """
        if address is None:
            address = ''
        address = str(address).strip()
        if len(address) > self.get_field('address2_deliver_to').max_length:
            return 'financial_account_sale_credit_note_create_103'
        self.cleaned_data['address2_deliver_to'] = address
        return None

    def validate_address3_deliver_to(self, address: Optional[str]) -> Optional[str]:
        """
        description: The third line of the geographic Address where the Sale Credit Note's items will be delivered to
        type: string
        required: false
        """
        if address is None:
            address = ''
        address = str(address).strip()
        if len(address) > self.get_field('address3_deliver_to').max_length:
            return 'financial_account_sale_credit_note_create_104'
        self.cleaned_data['address3_deliver_to'] = address
        return None

    def validate_city_deliver_to(self, city_deliver_to: Optional[str]) -> Optional[str]:
        """
        description: The city where the Sale Credit Note's items will be delivered to
        type: string
        """
        if city_deliver_to is None:
            city_deliver_to = ''
        city_deliver_to = str(city_deliver_to).strip()
        if len(city_deliver_to) == 0:
            return 'financial_account_sale_credit_note_create_105'
        if len(city_deliver_to) > self.get_field('city_deliver_to').max_length:
            return 'financial_account_sale_credit_note_create_106'
        self.cleaned_data['city_deliver_to'] = city_deliver_to
        return None

    def validate_contra_address_id(self, contra_address_id: Optional[int]) -> Optional[str]:
        """
        description: The id of the Address who the requesting User is issuing the Credit Note to
        type: integer
        """
        try:
            contra_address_id = int(cast(int, contra_address_id))
        except (TypeError, ValueError):
            return 'financial_account_sale_credit_note_create_107'
        response = Membership.address.read(
            token=self.request.user.token,
            pk=contra_address_id,
            span=self.span,
        )
        if response.status_code != 200:
            return 'financial_account_sale_credit_note_create_108'
        self.cleaned_data['contra_address_id'] = contra_address_id
        self.cleaned_data['contra_address'] = response.json()['content']
        return None

    def validate_contra_contact_id(self, contra_contact_id: Optional[int]) -> Optional[str]:
        """
        description: |
            The id of a User in the Contra Address who should be contacted with any queries about the Sale Credit Note
        type: integer
        required: false
        """
        contra_address_id = self.cleaned_data.get('contra_address_id')
        if contra_contact_id is None or contra_address_id is None:
            return None
        try:
            contra_contact_id = int(cast(int, contra_contact_id))
        except (TypeError, ValueError):
            return 'financial_account_sale_credit_note_create_109'
        response = Membership.user.read(
            token=self.request.user.token,
            pk=contra_contact_id,
            span=self.span,
        )
        if response.status_code != 200 or response.json()['content']['address']['id'] != contra_address_id:
            return 'financial_account_sale_credit_note_create_110'
        content = response.json()['content']
        full_name = content['first_name'] + ' ' + content['surname']
        self.cleaned_data['contra_contact'] = full_name
        return None

    def validate_country_id_deliver_to(self, country_id_deliver_to: Optional[int]) -> Optional[str]:
        """
        description: The id of the Country where the Sale Credit Note's items will be delivered to
        type: integer
        """
        try:
            country_id_deliver_to = int(cast(int, country_id_deliver_to))
        except (TypeError, ValueError):
            return 'financial_account_sale_credit_note_create_111'

        response = Membership.country.read(
            token=self.request.user.token,
            pk=country_id_deliver_to,
            span=self.span,
        )
        if response.status_code != 200:
            return 'financial_account_sale_credit_note_create_112'
        self.cleaned_data['country_id_deliver_to'] = country_id_deliver_to
        return None

    def validate_external_reference(self, external_reference: Optional[str]) -> Optional[str]:
        """
        description: The identifier for this Sale Credit Note in the Contra Address' referencing scheme
        type: string
        required: false
        """
        if external_reference is None:
            external_reference = ''
        external_reference = str(external_reference).strip()
        if len(external_reference) > self.get_field('external_reference').max_length:
            return 'financial_account_sale_credit_note_create_113'
        self.cleaned_data['external_reference'] = external_reference
        return None

    def validate_name_deliver_to(self, name_deliver_to: Optional[str]) -> Optional[str]:
        """
        description: The name of the company to deliver the Sale Credit Note's items to
        type: string
        """
        if name_deliver_to is None:
            name_deliver_to = ''
        name_deliver_to = str(name_deliver_to).strip()
        if len(name_deliver_to) == 0:
            return 'financial_account_sale_credit_note_create_114'
        if len(name_deliver_to) > self.get_field('name_deliver_to').max_length:
            return 'financial_account_sale_credit_note_create_115'
        self.cleaned_data['name_deliver_to'] = name_deliver_to
        return None

    def validate_narrative(self, narrative: Optional[str]) -> Optional[str]:
        """
        description: A summary of the Sale Credit Note and its items
        type: string
        """
        if narrative is None:
            narrative = ''
        narrative = str(narrative).strip()
        if len(narrative) > self.get_field('narrative').max_length:
            return 'financial_account_sale_credit_note_create_116'
        self.cleaned_data['narrative'] = narrative
        return None

    def validate_lines(self, lines: Optional[List[DEBIT]]) -> Optional[str]:
        """
        description: A collection of the amounts to debit each Nominal Account for this Account Sale Credit Note
        type: array
        items:
            type: object
            properties:
                description:
                    type: string
                exchange_rate:
                    type: string
                    format: decimal
                number:
                    type: integer
                part_number:
                    type: integer
                quantity:
                    type: string
                    format: decimal
                tax_rate:
                    type: string
                    format: decimal
                tax_amount:
                    type: string
                    format: decimal
                unit_price:
                    type: string
                    format: decimal
        """
        if 'contra_address_id' not in self.cleaned_data:
            return None

        if not isinstance(lines, list):
            return 'financial_account_sale_credit_note_create_117'

        account_numbers: Set[int] = set()
        tax_rate_ids: Set[int] = set()
        # Validate that the data is in the correct format
        for line in lines:
            if not isinstance(line, dict):
                return 'financial_account_sale_credit_note_create_118'

            try:
                description = cast(str, line['description'])
            except KeyError:
                return 'financial_account_sale_credit_note_create_119'
            if len(description) > NominalLedgerDebit._meta.get_field('description').max_length:
                return 'financial_account_sale_credit_note_create_138'

            try:
                line['exchange_rate'] = Decimal(str(line.get('exchange_rate', 1)))
            except InvalidOperation:
                return 'financial_account_sale_credit_note_create_120'

            try:
                number = int(cast(int, line['number']))
                if number not in range(0, 8000):
                    return 'financial_account_sale_credit_note_create_121'
                line['number'] = number
                account_numbers.add(number)
            except (KeyError, TypeError, ValueError):
                return 'financial_account_sale_credit_note_create_122'

            try:
                line['quantity'] = Decimal(str(line['quantity']))
            except (InvalidOperation, KeyError):
                return 'financial_account_sale_credit_note_create_123'

            try:
                tax_rate_id = int(cast(int, line['tax_rate_id']))
                line['tax_rate_id'] = tax_rate_id
                tax_rate_ids.add(tax_rate_id)
            except (KeyError, TypeError, ValueError):
                return 'financial_account_sale_credit_note_create_124'

            try:
                line['unit_price'] = Decimal(str(line['unit_price']))
            except (InvalidOperation, KeyError):
                return 'financial_account_sale_credit_note_create_125'

        # Make sure all the Nominal Accounts exist
        accounts = AddressNominalAccount.objects.filter(
            address_id=self.request.user.address['id'],
            global_nominal_account__nominal_account_number__in=account_numbers,
        )
        if len(accounts) != len(account_numbers):
            return 'financial_account_sale_credit_note_create_126'
        for a in accounts:
            if not a.global_nominal_account.valid_sales_account and \
                    a.global_nominal_account.nominal_account_number != reserved.VAT_CONTROL_ACCOUNT:
                return 'financial_account_sale_credit_note_create_127'

        # Make sure all the Tax Rates exist
        tax_rates = TaxRate.objects.filter(
            address_id=self.request.user.address['id'],
            id__in=tax_rate_ids,
        )
        if len(tax_rates) != len(tax_rate_ids):
            return 'financial_account_sale_credit_note_create_128'
        # Put the Tax Rates in a dictionary for easy access
        tax_rates = {obj.id: obj for obj in tax_rates}

        # Now that the data is valid, make sure the calculations are correct
        gross_amount = Decimal('0')
        tax_amount = Decimal('0')
        rounding_figure = Decimal('1.00')
        results: Deque = deque()
        for line in lines:
            # Calculate the transaction subtotals
            unit_price = cast(Decimal, line['unit_price'])
            quantity = cast(Decimal, line['quantity'])

            # Calculate the amount of the line
            amount = (unit_price * quantity).quantize(rounding_figure, rounding=ROUND_HALF_UP)

            # Calculate amounts and tax in the User's base currency
            exchange_rate = cast(Decimal, line['exchange_rate'])
            gross_amount += amount * exchange_rate

            # Calculate tax
            tax_rate = tax_rates[line['tax_rate_id']]
            tax_percent = Decimal(tax_rate.percent)
            tax_amount += amount * exchange_rate * tax_percent / 100

            results.append({
                'amount': amount,
                'description': line['description'],
                'exchange_rate': exchange_rate,
                'nominal_account_number': line['number'],
                'part_number': line.get('part_number', ''),
                'quantity': quantity,
                'tax_percent': tax_percent,
                'tax_rate': tax_rate,
                'unit_price': unit_price,
            })

        if gross_amount <= Decimal('0'):
            return 'financial_account_sale_credit_note_create_129'

        # Now go and get the description of the VAT and Debtor Control Accounts
        accounts = AddressNominalAccount.objects.filter(
            address_id=self.request.user.address['id'],
            global_nominal_account__nominal_account_number__in=[
                reserved.VAT_CONTROL_ACCOUNT,
                reserved.DEBTOR_CONTROL_ACCOUNT,
            ],
        )
        vat_description = str()
        debtor_description = str()
        for a in accounts:
            if a.global_nominal_account.nominal_account_number == reserved.VAT_CONTROL_ACCOUNT:
                vat_description = a.description
            elif a.global_nominal_account.nominal_account_number == reserved.DEBTOR_CONTROL_ACCOUNT:
                debtor_description = a.description

        # Add an entry for total VAT
        results.append({
            'amount': tax_amount.quantize(rounding_figure, rounding=ROUND_HALF_UP),
            'description': vat_description,
            'exchange_rate': 1,
            'nominal_account_number': reserved.VAT_CONTROL_ACCOUNT,
            'quantity': 0,
            'unit_price': 0,
        })
        self.cleaned_data['debits'] = results
        self.cleaned_data['credit'] = {
            'amount': (gross_amount + tax_amount).quantize(rounding_figure, rounding=ROUND_HALF_UP),
            'description': debtor_description,
            'exchange_rate': 1,
            'nominal_account_number': reserved.DEBTOR_CONTROL_ACCOUNT,
            'quantity': 0,
            'unit_price': 0,
        }
        return None

    def validate_postcode_deliver_to(self, postcode_deliver_to: Optional[str]) -> Optional[str]:
        """
        description: The postcode that the Sale Credit Note's items will be delivered to
        type: string
        required: false
        """
        if postcode_deliver_to is None:
            postcode_deliver_to = ''
        postcode_deliver_to = str(postcode_deliver_to).strip()
        if len(postcode_deliver_to) > self.get_field('postcode_deliver_to').max_length:
            return 'financial_account_sale_credit_note_create_130'
        self.cleaned_data['postcode_deliver_to'] = postcode_deliver_to
        return None

    def validate_report_template_id(self, report_template_id: Optional[int]) -> Optional[str]:
        """
        description: The id of the Report Template to use when printing the Sale Credit Note
        type: integer
        """
        if report_template_id is None:
            return None
        try:
            report_template_id = int(cast(int, report_template_id))
        except (TypeError, ValueError):
            return 'financial_account_sale_credit_note_create_131'
        response = Reporting.report_template.read(
            token=self.request.user.token,
            pk=report_template_id,
            span=self.span,
        )
        if response.status_code != 200:
            return 'financial_account_sale_credit_note_create_132'
        if response.json()['content']['idTransactionType'] != 11003:
            return 'financial_account_sale_credit_note_create_133'
        self.cleaned_data['report_template_id'] = report_template_id
        return None

    def validate_subdivision_id_deliver_to(self, subdivision_id_deliver_to: Optional[int]) -> Optional[str]:
        """
        description: The id of the Subdivision where the Sale Credit Note's items will be delivered to
        type: integer
        required: false
        """
        if subdivision_id_deliver_to is None or 'country_id_deliver_to' not in self.cleaned_data:
            return None
        try:
            subdivision_id_deliver_to = int(cast(int, subdivision_id_deliver_to))
        except (TypeError, ValueError):
            return 'financial_account_sale_credit_note_create_134'

        response = Membership.subdivision.read(
            token=self.request.user.token,
            pk=subdivision_id_deliver_to,
            country_id=self.cleaned_data['country_id_deliver_to'],
            span=self.span,
        )
        if response.status_code != 200:
            return 'financial_account_sale_credit_note_create_135'
        self.cleaned_data['subdivision_id_deliver_to'] = subdivision_id_deliver_to
        return None

    def validate_transaction_date(self, date: Optional[str]) -> Optional[str]:
        """
        description: The date that the Sale Credit Note was issued
        type: string
        """
        try:
            transaction_date = datetime.strptime(str(date).split('T')[0], '%Y-%m-%d').date()
        except (TypeError, ValueError):
            return 'financial_account_sale_credit_note_create_136'
        obj = NominalLedger.period_end.filter(
            address_id=self.request.user.address['id'],
            transaction_date__gte=transaction_date,
        )
        if obj.exists():
            return 'financial_account_sale_credit_note_create_137'
        self.cleaned_data['transaction_date'] = transaction_date
        return None


class AccountSaleCreditNoteUpdateController(ControllerBase):
    """
    Validate User data to update a Nominal Ledger record for an Account Sale Credit Note transaction
    """

    class Meta(ControllerBase.Meta):
        """
        Override some of the ControllerBase.Meta fields to make them more specific for this Controller
        """
        model = NominalLedger
        validation_order = (
            'external_reference',
        )

    def validate_external_reference(self, external_reference: Optional[str]) -> Optional[str]:
        """
        description: The identifier for this Sale Credit Note in the Contra Address' referencing scheme
        type: string
        required: false
        """
        if external_reference is None:
            external_reference = ''
        external_reference = str(external_reference).strip()
        if len(external_reference) > self.get_field('external_reference').max_length:
            return 'financial_account_sale_credit_note_update_101'
        self.cleaned_data['external_reference'] = external_reference
        return None


class AccountSaleCreditNoteContraCreateController(ControllerBase):
    """
    Validate User data to create a new Nominal Ledger record for an Account Sale Credit Note transaction
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
            'lines',
        )

    def validate_narrative(self, narrative: Optional[str]) -> Optional[str]:
        """
        description: A summary of the Sale Credit Note and its items
        type: string
        """
        if narrative is None:
            narrative = ''
        narrative = str(narrative).strip()
        if len(narrative) > self.get_field('narrative').max_length:
            return 'financial_account_sale_credit_note_contra_create_101'
        self.cleaned_data['narrative'] = narrative
        return None

    def validate_report_template_id(self, report_template_id: Optional[int]) -> Optional[str]:
        """
        description: The id of the Report Template to use when printing the Sale Credit Note
        type: integer
        """
        if report_template_id is None:
            return None
        try:
            report_template_id = int(cast(int, report_template_id))
        except (TypeError, ValueError):
            return 'financial_account_sale_credit_note_contra_create_102'
        response = Reporting.report_template.read(
            token=self.request.user.token,
            pk=report_template_id,
            span=self.span,
        )
        if response.status_code != 200:
            return 'financial_account_sale_credit_note_contra_create_103'
        if response.json()['content']['idTransactionType'] != 11003:
            return 'financial_account_sale_credit_note_contra_create_104'
        self.cleaned_data['report_template_id'] = report_template_id
        return None

    def validate_transaction_date(self, date: Optional[str]) -> Optional[str]:
        """
        description: The date that the Sale Credit Note was issued
        type: string
        """
        try:
            transaction_date = datetime.strptime(str(date).split('T')[0], '%Y-%m-%d').date()
        except (TypeError, ValueError):
            return 'financial_account_sale_credit_note_contra_create_105'
        obj = NominalLedger.period_end.filter(
            address_id=self.request.user.address['id'],
            transaction_date__gte=transaction_date,
        )
        if obj.exists():
            return 'financial_account_sale_credit_note_contra_create_106'
        self.cleaned_data['transaction_date'] = transaction_date
        return None

    def validate_tsn(self, tsn: Optional[int]) -> Optional[str]:
        """
        description: |
            The Transaction Sequence Number of an Account Purchase Debit Note from the Contra Address, from which a new
            Account Sale Credit Note will be made
        type: integer
        """
        try:
            tsn = int(cast(int, tsn))
        except (TypeError, ValueError):
            return 'financial_account_sale_credit_note_contra_create_107'

        try:
            # Fetch the Account Sale Credit Note that the Account Purchase Debit Note is being created in response to
            debit_note = NominalLedger.account_purchase_debit_notes.get(
                tsn=tsn,
                address_id=self.address_id,
                contra_address_id=self.request.user.address['id'],
            )
        except NominalLedger.DoesNotExist:
            return 'financial_account_sale_credit_note_contra_create_108'

        if debit_note.contra_nominal_ledger is not None:
            return 'financial_account_sale_credit_note_contra_create_109'

        self.cleaned_data['contra_nominal_ledger'] = debit_note
        return None

    def validate_lines(self, lines: Optional[DEBIT]) -> Optional[str]:
        """
        description: |
            A collection of the amounts to debit each Nominal Account for this Account Sale Credit Note
        type: array
        items:
            type: object
            properties:
                description:
                    type: string
                exchange_rate:
                    type: string
                    format: decimal
                number:
                    type: integer
                part_number:
                    type: string
                quantity:
                    type: string
                    format: decimal
                tax_rate:
                    type: string
                    format: decimal
                unit_price:
                    type: string
                    format: decimal
        """
        if not isinstance(lines, list):
            return 'financial_account_sale_credit_note_contra_create_110'

        if 'contra_nominal_ledger' not in self.cleaned_data:
            return None
        debit_note = self.cleaned_data['contra_nominal_ledger']

        # make sure each transaction is accounted for. One extra credit is created for VAT when an Account Purchase
        # Debit Note is made
        credits = debit_note.credits.all()
        if len(lines) != len(credits) - 1:
            return 'financial_account_sale_credit_note_contra_create_111'

        account_numbers: Set[int] = set()
        tax_rate_ids: Set[int] = set()
        for line in lines:
            if not isinstance(line, dict):
                return 'financial_account_sale_credit_note_contra_create_112'

            try:
                description = cast(str, line['description'])
            except KeyError:
                return 'financial_account_sale_credit_note_contra_create_113'
            if len(description) > NominalLedgerDebit._meta.get_field('description').max_length:
                return 'financial_account_sale_credit_note_contra_create_124'

            try:
                line['exchange_rate'] = Decimal(str(line.get('exchange_rate', 1)))
            except InvalidOperation:
                return 'financial_account_sale_credit_note_contra_create_114'

            try:
                number = int(cast(int, line['number']))
                if number not in range(0, 8000):
                    return 'financial_account_sale_credit_note_contra_create_115'
                line['number'] = number
                account_numbers.add(number)
            except (KeyError, TypeError, ValueError):
                return 'financial_account_sale_credit_note_contra_create_116'

            try:
                line['quantity'] = Decimal(str(line['quantity']))
            except (InvalidOperation, KeyError):
                return 'financial_account_sale_credit_note_contra_create_117'

            try:
                tax_rate_id = int(cast(int, line['tax_rate_id']))
                line['tax_rate_id'] = tax_rate_id
                tax_rate_ids.add(tax_rate_id)
            except (KeyError, TypeError, ValueError):
                return 'financial_account_sale_credit_note_contra_create_118'

            try:
                line['unit_price'] = Decimal(str(line['unit_price']))
            except (InvalidOperation, KeyError):
                return 'financial_account_sale_credit_note_contra_create_119'

        # Fetch all the Nominal Accounts
        accounts = AddressNominalAccount.objects.filter(
            address_id=self.request.user.address['id'],
            global_nominal_account__nominal_account_number__in=account_numbers,
        )
        if len(accounts) != len(account_numbers):
            return 'financial_account_sale_credit_note_contra_create_120'

        for a in accounts:
            if not a.global_nominal_account.valid_sales_account:
                return 'financial_account_sale_credit_note_contra_create_121'

        # Fetch all the Tax Rate records
        tax_rates = TaxRate.objects.filter(
            address_id=self.request.user.address['id'],
            id__in=tax_rate_ids,
        )
        if len(tax_rates) != len(tax_rate_ids):
            return 'financial_account_sale_credit_note_contra_create_122'
        # Put the Tax Rates in a dictionary for easy access
        tax_rates = {obj.id: obj for obj in tax_rates}

        # Now make sure the line matches one of the credits from the Account Purchase Debit Note
        tax_amount = Decimal('0')
        gross_amount = Decimal('0')
        results: Deque[DEBIT] = deque()
        for c in credits:
            if c.nominal_account_number == reserved.VAT_CONTROL_ACCOUNT:
                # We can't copy the VAT line from the contra. We need to use the rest of the lines to calculate it in
                # the currency of the requesting User's Address
                continue
            match_found = False
            for line in lines:
                # Get the tax rate for the line
                tax_rate = tax_rates[line['tax_rate_id']]

                # Find one of the sent lines that matches the credit line
                if c.description == line['description'] and c.unit_price == line['unit_price'] and \
                        c.quantity == line['quantity'] and c.tax_percent == tax_rate.percent:
                    match_found = True
                    amount = Decimal(c.amount).quantize(Decimal('1.00'), rounding=ROUND_HALF_UP)
                    exchange_rate = cast(Decimal, line['exchange_rate'])
                    results.append({
                        'amount': amount,
                        'description': c.description,
                        'exchange_rate': exchange_rate,
                        'nominal_account_number': line['number'],
                        'part_number': c.part_number,
                        'quantity': c.quantity,
                        'tax_percent': tax_rate.percent,
                        'tax_rate': tax_rate,
                        'unit_price': c.unit_price,
                    })
                    gross_amount += amount * exchange_rate
                    tax_amount += amount * exchange_rate * tax_rate.percent / 100
                    break

            if not match_found:
                return 'financial_account_sale_credit_note_contra_create_123'

        # Get the descriptions of the control accounts
        control_accounts = AddressNominalAccount.objects.filter(
            address_id=self.request.user.address['id'],
            global_nominal_account__nominal_account_number__in=[
                reserved.VAT_CONTROL_ACCOUNT,
                reserved.DEBTOR_CONTROL_ACCOUNT,
            ],
        )
        vat_description = str()
        debtor_description = str()
        for a in control_accounts:
            if a.global_nominal_account.nominal_account_number == reserved.VAT_CONTROL_ACCOUNT:
                vat_description = a.description
            if a.global_nominal_account.nominal_account_number == reserved.DEBTOR_CONTROL_ACCOUNT:
                debtor_description = a.description

        # Create a line for VAT
        results.append({
            'amount': tax_amount.quantize(Decimal('1.00'), rounding=ROUND_HALF_UP),
            'description': vat_description,
            'nominal_account_number': reserved.VAT_CONTROL_ACCOUNT,
            'quantity': 0,
            'unit_price': 0,
        })
        self.cleaned_data['debits'] = results

        # Add in one credit for the Debtors Control Account
        self.cleaned_data['credit'] = {
            'amount': (gross_amount + tax_amount).quantize(Decimal('1.00'), rounding=ROUND_HALF_UP),
            'description': debtor_description,
            'exchange_rate': 1,
            'nominal_account_number': reserved.DEBTOR_CONTROL_ACCOUNT,
            'part_number': '',
            'quantity': 0,
            'unit_price': 0,
        }
        return None
