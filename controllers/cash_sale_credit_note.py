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
from financial.models import (
    AddressNominalAccount,
    NominalContra,
    NominalLedger,
    PaymentMethod,
    TaxRate,
)
from financial.models.nominal_ledger_debit import NominalLedgerDebit


__all__ = [
    'CashSaleCreditNoteCreateController',
    'CashSaleCreditNoteUpdateController',
    'CashSaleCreditNoteContraCreateController',
]

DEBIT = Dict[str, Union[int, str, Decimal]]
VALID_ACCOUNT_RANGE = range(1000, 3000)


class CashSaleCreditNoteCreateController(ControllerBase):
    """
    Validate User data to create a new Nominal Ledger record for a Cash Sale Credit Note transaction
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
            'lines',
            'name_deliver_to',
            'narrative',
            'payment_method_id',
            'postcode_deliver_to',
            'report_template_id',
            'subdivision_id_deliver_to',
            'transaction_date',
        )

    def validate_address1_deliver_to(self, address: Optional[str]) -> Optional[str]:
        """
        description: The first line of the geographic address to deliver the items of the Cash Sale Credit Note to
        type: string
        """
        if address is None:
            address = ''
        address = str(address).strip()
        if len(address) == 0:
            return 'financial_cash_sale_credit_note_create_101'
        if len(address) > self.get_field('address1_deliver_to').max_length:
            return 'financial_cash_sale_credit_note_create_102'
        self.cleaned_data['address1_deliver_to'] = address
        return None

    def validate_address2_deliver_to(self, address: Optional[str]) -> Optional[str]:
        """
        description: The second line of the geographic address to deliver the items of the Cash Sale Credit Note to
        type: string
        required: false
        """
        if address is None:
            address = ''
        address = str(address).strip()
        if len(address) > self.get_field('address2_deliver_to').max_length:
            return 'financial_cash_sale_credit_note_create_103'
        self.cleaned_data['address2_deliver_to'] = address
        return None

    def validate_address3_deliver_to(self, address: Optional[str]) -> Optional[str]:
        """
        description: The third line of the geographic address to deliver the items of the Cash Sale Credit Note to
        type: string
        required: false
        """
        if address is None:
            address = ''
        address = str(address).strip()
        if len(address) > self.get_field('address3_deliver_to').max_length:
            return 'financial_cash_sale_credit_note_create_104'
        self.cleaned_data['address3_deliver_to'] = address
        return None

    def validate_city_deliver_to(self, city_deliver_to: Optional[str]) -> Optional[str]:
        """
        description: The city where the Cash Sale Credit Note's items will be delivered to
        type: string
        """
        if city_deliver_to is None:
            city_deliver_to = ''
        city_deliver_to = str(city_deliver_to).strip()
        if len(city_deliver_to) == 0:
            return 'financial_cash_sale_credit_note_create_105'
        if len(city_deliver_to) > self.get_field('city_deliver_to').max_length:
            return 'financial_cash_sale_credit_note_create_106'
        self.cleaned_data['city_deliver_to'] = city_deliver_to
        return None

    def validate_contra_address_id(self, contra_address_id: Optional[int]) -> Optional[str]:
        """
        description: The id of the Address who the requesting User is paying money back to
        type: integer
        """
        try:
            contra_address_id = int(cast(int, contra_address_id))
        except (TypeError, ValueError):
            return 'financial_cash_sale_credit_note_create_107'
        response = Membership.address.read(
            token=self.request.user.token,
            pk=contra_address_id,
            span=self.span,
        )
        if response.status_code != 200:
            return 'financial_cash_sale_credit_note_create_108'
        self.cleaned_data['contra_address_id'] = contra_address_id
        self.cleaned_data['contra_address'] = response.json()['content']
        return None

    def validate_contra_contact_id(self, contra_contact_id: Optional[int]) -> Optional[str]:
        """
        description: |
            The id of a User in the Contra Address to contact with inquiries about the Cash Sale Credit Note
        type: integer
        required: false
        """
        if contra_contact_id is None:
            return None
        try:
            contra_contact_id = int(cast(int, contra_contact_id))
        except (TypeError, ValueError):
            return 'financial_cash_sale_credit_note_create_109'

        if 'contra_address_id' not in self.cleaned_data:
            return None
        contra_address_id = self.cleaned_data['contra_address_id']

        response = Membership.user.read(
            token=self.request.user.token,
            pk=contra_contact_id,
            span=self.span,
        )
        if response.status_code != 200 or response.json()['content']['address']['id'] != contra_address_id:
            return 'financial_cash_sale_credit_note_create_110'
        content = response.json()['content']
        full_name = content['first_name'] + ' ' + content['surname']
        self.cleaned_data['contra_contact'] = full_name
        return None

    def validate_country_id_deliver_to(self, country_id_deliver_to: Optional[int]) -> Optional[str]:
        """
        description: The id of the Country where the Cash Sale Credit Note items will be delivered to
        type: integer
        """
        try:
            country_id_deliver_to = int(cast(int, country_id_deliver_to))
        except (TypeError, ValueError):
            return 'financial_cash_sale_credit_note_create_111'

        response = Membership.country.read(
            token=self.request.user.token,
            pk=country_id_deliver_to,
            span=self.span,
        )
        if response.status_code != 200:
            return 'financial_cash_sale_credit_note_create_112'
        self.cleaned_data['country_id_deliver_to'] = country_id_deliver_to
        return None

    def validate_external_reference(self, external_reference: Optional[str]) -> Optional[str]:
        """
        description: The identifier for this Cash Sale Credit Note in the Contra Address' referencing scheme
        type: string
        required: false
        """
        if external_reference is None:
            external_reference = ''
        external_reference = str(external_reference).strip()
        if len(external_reference) > self.get_field('external_reference').max_length:
            return 'financial_cash_sale_credit_note_create_113'
        self.cleaned_data['external_reference'] = external_reference
        return None

    def validate_lines(self, lines: Optional[List[DEBIT]]) -> Optional[str]:
        """
        description: A collection of the amounts to debit to each Nominal Account for this Cash Sale Credit Note
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
                tax_rate_id:
                    type: integer
                unit_price:
                    type: string
                    format: decimal
        """
        if not isinstance(lines, list):
            return 'financial_cash_sale_credit_note_create_114'

        if 'contra_address_id' not in self.cleaned_data:
            return None

        account_numbers: Set[int] = set()
        tax_rate_ids: Set[int] = set()
        for line in lines:
            if not isinstance(line, dict):
                return 'financial_cash_sale_credit_note_create_115'

            try:
                description = cast(str, line['description'])
            except KeyError:
                return 'financial_cash_sale_credit_note_create_116'
            if len(description) > NominalLedgerDebit._meta.get_field('description').max_length:
                return 'financial_cash_sale_credit_note_create_143'

            try:
                line['exchange_rate'] = Decimal(str(line.get('exchange_rate', 1)))
            except InvalidOperation:
                return 'financial_cash_sale_credit_note_create_117'

            try:
                number = int(cast(int, line['number']))
                if number not in range(8000):
                    return 'financial_cash_sale_credit_note_create_118'
                line['number'] = number
                account_numbers.add(number)
            except (KeyError, TypeError, ValueError):
                return 'financial_cash_sale_credit_note_create_119'

            try:
                line['quantity'] = Decimal(str(line['quantity']))
            except (InvalidOperation, KeyError):
                return 'financial_cash_sale_credit_note_create_120'

            try:
                tax_rate_id = int(cast(int, line['tax_rate_id']))
                line['tax_rate_id'] = tax_rate_id
                tax_rate_ids.add(tax_rate_id)
            except (KeyError, TypeError, ValueError):
                return 'financial_cash_sale_credit_note_create_121'

            try:
                line['unit_price'] = Decimal(str(line['unit_price']))
            except (InvalidOperation, KeyError):
                return 'financial_cash_sale_credit_note_create_122'

        # Make sure all the Nominal Accounts exist
        accounts = AddressNominalAccount.objects.filter(
            address_id=self.request.user.address['id'],
            global_nominal_account__nominal_account_number__in=account_numbers,
        )
        if len(accounts) != len(account_numbers):
            return 'financial_cash_sale_credit_note_create_123'
        for a in accounts:
            if not a.global_nominal_account.valid_sales_account and \
                    a.global_nominal_account.nominal_account_number != reserved.VAT_CONTROL_ACCOUNT:
                return 'financial_cash_sale_credit_note_create_124'

        # Make sure all the Tax Rates exist
        tax_rates = TaxRate.objects.filter(
            address_id=self.request.user.address['id'],
            id__in=tax_rate_ids,
        )
        if len(tax_rates) != len(tax_rate_ids):
            return 'financial_cash_sale_credit_note_create_125'
        # Put the Tax Rates in a dictionary for easy access
        tax_rates = {obj.id: obj for obj in tax_rates}

        # Now that the data is valid, calculate the transaction and tax amounts
        gross_amount = Decimal('0')
        tax_amount = Decimal('0')
        rounding_figure = Decimal('1.00')
        results: Deque[DEBIT] = deque()
        for line in lines:
            # Calculate the transaction subtotals
            unit_price = cast(Decimal, line['unit_price'])
            quantity = cast(Decimal, line['quantity'])

            # Calculate the amount of the line
            amount = (unit_price * quantity).quantize(rounding_figure, rounding=ROUND_HALF_UP)

            # Calculate the amounts and tax in the User's base currency
            exchange_rate = cast(Decimal, line['exchange_rate'])
            gross_amount += amount * exchange_rate

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
            return 'financial_cash_sale_credit_note_create_126'

        # Now go and get the description of the VAT Control Account
        vat_description = AddressNominalAccount.objects.values_list(
            'description',
            flat=True,
        ).get(
            address_id=self.request.user.address['id'],
            global_nominal_account__nominal_account_number=reserved.VAT_CONTROL_ACCOUNT,
        )

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
        # Make a credit for the Nominal Account specified by the `payment_method_id`
        self.cleaned_data['credit'] = {
            'amount': (gross_amount + tax_amount).quantize(rounding_figure, rounding=ROUND_HALF_UP),
            'exchange_rate': 1,
            'quantity': 0,
            'unit_price': 0,
        }
        return None

    def validate_name_deliver_to(self, name_deliver_to: Optional[str]) -> Optional[str]:
        """
        description: The name of the company to deliver the Cash Sale Credit Note's items to
        type: string
        """
        if name_deliver_to is None:
            name_deliver_to = ''
        name_deliver_to = str(name_deliver_to).strip()
        if len(name_deliver_to) == 0:
            return 'financial_cash_sale_credit_note_create_127'
        if len(name_deliver_to) > self.get_field('name_deliver_to').max_length:
            return 'financial_cash_sale_credit_note_create_128'
        self.cleaned_data['name_deliver_to'] = name_deliver_to
        return None

    def validate_narrative(self, narrative: Optional[str]) -> Optional[str]:
        """
        description: A summary of the Sale Credit Note and its items
        type: string
        required: false
        """
        if narrative is None:
            narrative = ''
        narrative = str(narrative).strip()
        if len(narrative) > self.get_field('narrative').max_length:
            return 'financial_cash_sale_credit_note_create_129'
        self.cleaned_data['narrative'] = narrative
        return None

    def validate_payment_method_id(self, payment_method_id: Optional[int]) -> Optional[str]:
        """
        description: |
            How the requesting User intends to pay the Credit Note. This will determine what Nominal Account will be
            debited by checking the Nominal Contra records
        type: integer
        """
        try:
            payment_method_id = int(cast(int, payment_method_id))
        except (TypeError, ValueError):
            return 'financial_cash_sale_credit_note_create_130'

        try:
            PaymentMethod.objects.get(
                id=payment_method_id,
                member_id=self.request.user.member['id'],
            )
        except PaymentMethod.DoesNotExist:
            return 'financial_cash_sale_credit_note_create_131'

        # Find out which Nominal Account will be debited by checking the Nominal Contras
        try:
            nominal_account_id = NominalContra.objects.values_list('global_nominal_account_id').get(
                payment_method_id=payment_method_id,
                transaction_type_id=11001,
            )
        except NominalContra.DoesNotExist:
            return 'financial_cash_sale_credit_note_create_132'

        # Make sure the Nominal Account pointed to by the Nominal Contra has an Address Nominal Account set up for the
        # User's Address
        try:
            address_account = AddressNominalAccount.objects.get(
                address_id=self.request.user.address['id'],
                global_nominal_account_id=nominal_account_id,
            )
        except AddressNominalAccount.DoesNotExist:
            return 'financial_cash_sale_credit_note_create_133'

        if address_account.global_nominal_account.nominal_account_number not in VALID_ACCOUNT_RANGE:
            return 'financial_cash_sale_credit_note_create_134'

        self.cleaned_data['address_account'] = address_account
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
            return 'financial_cash_sale_credit_note_create_135'
        self.cleaned_data['postcode_deliver_to'] = postcode_deliver_to
        return None

    def validate_report_template_id(self, report_template_id: Optional[int]) -> Optional[str]:
        """
        description: The id of the Report Template to use when printing the Cash Sale Credit Note
        type: integer
        """
        if report_template_id is None:
            return None
        try:
            report_template_id = int(cast(int, report_template_id))
        except (TypeError, ValueError):
            return 'financial_cash_sale_credit_note_create_136'
        response = Reporting.report_template.read(
            token=self.request.user.token,
            pk=report_template_id,
            span=self.span,
        )
        if response.status_code != 200:
            return 'financial_cash_sale_credit_note_create_137'
        if response.json()['content']['idTransactionType'] != 11001:
            return 'financial_cash_sale_credit_note_create_138'
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
            return 'financial_cash_sale_credit_note_create_139'

        response = Membership.subdivision.read(
            token=self.request.user.token,
            pk=subdivision_id_deliver_to,
            country_id=self.cleaned_data['country_id_deliver_to'],
            span=self.span,
        )
        if response.status_code != 200:
            return 'financial_cash_sale_credit_note_create_140'
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
            return 'financial_cash_sale_credit_note_create_141'
        obj = NominalLedger.period_end.filter(
            address_id=self.request.user.address['id'],
            transaction_date__gte=transaction_date,
        )
        if obj.exists():
            return 'financial_cash_sale_credit_note_create_142'
        self.cleaned_data['transaction_date'] = transaction_date
        return None


class CashSaleCreditNoteUpdateController(ControllerBase):
    """
    Validate User data to update an existing Nominal Ledger record for a Cash Sale Credit Note transaction
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
        description: The identifier for this Cash Sale Credit Note in the Contra Address' referencing scheme
        type: string
        required: false
        """
        if external_reference is None:
            return None
        external_reference = str(external_reference).strip()
        if len(external_reference) > self.get_field('external_reference').max_length:
            return 'financial_cash_sale_credit_note_update_101'
        self.cleaned_data['external_reference'] = external_reference
        return None


class CashSaleCreditNoteContraCreateController(ControllerBase):
    """
    Validate User data to create a Nominal Ledger record for a Cash Sale Credit Note transaction
    """

    class Meta(ControllerBase.Meta):
        """
        Override some of the ControllerBase.Meta fields to make them more specific for this Controller
        """
        model = NominalLedger
        validation_order = (
            'payment_method_id',
            'report_template_id',
            'transaction_date',
            'tsn',
            'lines',
        )

    def validate_payment_method_id(self, payment_method_id: Optional[int]) -> Optional[str]:
        """
        description: |
            How the requesting User intends to pay the Credit Note. This will determine what Nominal Account will be
            debited by checking the Nominal Contra records
        type: integer
        """
        try:
            payment_method_id = int(cast(int, payment_method_id))
        except (TypeError, ValueError):
            return 'financial_cash_sale_credit_note_contra_create_101'

        try:
            PaymentMethod.objects.get(
                id=payment_method_id,
                member_id=self.request.user.member['id'],
            )
        except PaymentMethod.DoesNotExist:
            return 'financial_cash_sale_credit_note_contra_create_102'

        try:
            nominal_account_id = NominalContra.objects.values_list('global_nominal_account_id').get(
                payment_method_id=payment_method_id,
                transaction_type_id=11001,
            )
        except NominalContra.DoesNotExist:
            return 'financial_cash_sale_credit_note_contra_create_103'

        # Make sure the Nominal Account pointed to by the Nominal Contra has an Address Nominal Account set up for the
        # User's Address
        try:
            address_account = AddressNominalAccount.objects.get(
                address_id=self.request.user.address['id'],
                global_nominal_account_id=nominal_account_id,
            )
        except AddressNominalAccount.DoesNotExist:
            return 'financial_cash_sale_credit_note_contra_create_104'

        if address_account.global_nominal_account.nominal_account_number not in VALID_ACCOUNT_RANGE:
            return 'financial_cash_sale_credit_note_contra_create_105'

        self.cleaned_data['address_account'] = address_account
        return None

    def validate_report_template_id(self, report_template_id: Optional[int]) -> Optional[str]:
        """
        description: The id of the Report Template to use when printing the Cash Sale Credit Note
        type: integer
        """
        try:
            report_template_id = int(cast(int, report_template_id))
        except (TypeError, ValueError):
            return 'financial_cash_sale_credit_note_contra_create_106'

        response = Reporting.report_template.read(
            token=self.request.user.token,
            pk=report_template_id,
        )
        if response.status_code != 200:
            return 'financial_cash_sale_credit_note_contra_create_107'
        if response.json()['content']['idTransactionType'] != 11001:
            return 'financial_cash_sale_credit_note_contra_create_108'

        self.cleaned_data['report_template_id'] = report_template_id
        return None

    def validate_transaction_date(self, date: Optional[str]) -> Optional[str]:
        """
        description: The date that the Cash Sale Credit Note was created
        type: string
        """
        try:
            transaction_date = datetime.strptime(str(date).split('T')[0], '%Y-%m-%d').date()
        except (TypeError, ValueError):
            return 'financial_cash_sale_credit_note_contra_create_109'
        obj = NominalLedger.period_end.filter(
            address_id=self.request.user.address['id'],
            transaction_date__gte=transaction_date,
        )
        if obj.exists():
            return 'financial_cash_sale_credit_note_contra_create_110'
        self.cleaned_data['transaction_date'] = transaction_date
        return None

    def validate_tsn(self, tsn: Optional[int]) -> Optional[str]:
        """
        description: The Transaction Sequence Number of a Cash Purchase Debit Note in the specified Contra Address
        type: integer
        """
        try:
            tsn = int(cast(int, tsn))
        except (TypeError, ValueError):
            return 'financial_cash_sale_credit_note_contra_create_111'

        try:
            debit_note = NominalLedger.cash_purchase_debit_notes.get(
                tsn=tsn,
                address_id=self.address_id,
                contra_address_id=self.request.user.address['id'],
            )
        except NominalLedger.DoesNotExist:
            return 'financial_cash_sale_credit_note_contra_create_112'

        if debit_note.contra_nominal_ledger is not None:
            return 'financial_cash_sale_credit_note_contra_create_113'

        self.cleaned_data['contra_nominal_ledger'] = debit_note
        return None

    def validate_lines(self, lines: Optional[DEBIT]) -> Optional[str]:
        """
        description: A collection of the amounts to debit to each Nominal Account for this Cash Sale Credit Note
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
                tax_rate_id:
                    type: integer
                unit_price:
                    type: string
                    format: decimal
        """
        if not isinstance(lines, list):
            return 'financial_cash_sale_credit_note_contra_create_114'

        if 'contra_nominal_ledger' not in self.cleaned_data:
            return None
        debit_note = self.cleaned_data['contra_nominal_ledger']

        # Make sure each line in the transaction is accounted for. One extra credit entry is made for VAT when a Cash
        # Purchase Debit Note gets created
        credits = debit_note.credits.all()
        if len(lines) != len(credits) - 1:
            return 'financial_cash_sale_credit_note_contra_create_115'

        account_numbers: Set[int] = set()
        tax_rate_ids: Set[int] = set()
        for line in lines:
            if not isinstance(line, dict):
                return 'financial_cash_sale_credit_note_contra_create_116'

            try:
                description = cast(str, line['description'])
            except KeyError:
                return 'financial_cash_sale_credit_note_contra_create_117'
            if len(description) > NominalLedgerDebit._meta.get_field('description').max_length:
                return 'financial_cash_sale_credit_note_contra_create_128'

            try:
                line['exchange_rate'] = Decimal(str(line.get('exchange_rate', 1)))
            except InvalidOperation:
                return 'financial_cash_sale_credit_note_contra_create_118'

            try:
                number = int(cast(int, line['number']))
                if number not in range(8000):
                    return 'financial_cash_sale_credit_note_contra_create_119'
                line['number'] = number
                account_numbers.add(number)
            except (KeyError, TypeError, ValueError):
                return 'financial_cash_sale_credit_note_contra_create_120'

            try:
                line['quantity'] = Decimal(str(line['quantity']))
            except (InvalidOperation, KeyError):
                return 'financial_cash_sale_credit_note_contra_create_121'

            try:
                tax_rate_id = int(cast(int, line['tax_rate_id']))
                line['tax_rate_id'] = tax_rate_id
                tax_rate_ids.add(tax_rate_id)
            except (KeyError, TypeError, ValueError):
                return 'financial_cash_sale_credit_note_contra_create_122'

            try:
                line['unit_price'] = Decimal(str(line['unit_price']))
            except (InvalidOperation, KeyError):
                return 'financial_cash_sale_credit_note_contra_create_123'

        # Make sure all the Nominal Accounts exist
        accounts = AddressNominalAccount.objects.filter(
            address_id=self.request.user.address['id'],
            global_nominal_account__nominal_account_number__in=account_numbers,
        )
        if len(accounts) != len(account_numbers):
            return 'financial_cash_sale_credit_note_contra_create_124'
        for a in accounts:
            if not a.global_nominal_account.valid_sales_account:
                return 'financial_cash_sale_credit_note_contra_create_125'

        # Make sure all the Tax Rates exist
        tax_rates = TaxRate.objects.filter(
            address_id=self.request.user.address['id'],
            id__in=tax_rate_ids,
        )
        if len(tax_rates) != len(tax_rate_ids):
            return 'financial_cash_sale_credit_note_contra_create_126'
        # Put the Tax Rates in a dictionary for easy access
        tax_rates = {obj.id: obj for obj in tax_rates}

        # Now make sure each line matches one of the credits from the Cash Sale Credit Note
        gross_amount = Decimal('0')
        tax_amount = Decimal('0')
        results: Deque[DEBIT] = deque()
        for c in credits:
            if c.nominal_account_number == reserved.VAT_CONTROL_ACCOUNT:
                # We can't take the VAT line directly from the contra. The VAT mus tbe calculated from the lines in the
                # base currency of the requesting User's Address
                continue
            match_found = False
            for line in lines:
                # Get the Tax Rate for this line
                tax_rate = tax_rates[line['tax_rate_id']]

                if line['description'] == c.description and line['quantity'] == c.quantity and \
                        line['unit_price'] == c.unit_price and tax_rate.percent == c.tax_percent:
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
                return 'financial_cash_sale_credit_note_contra_create_127'

        # Get the description from the VAT Control Account
        vat_description = AddressNominalAccount.objects.values_list(
            'description',
            flat=True,
        ).get(
            address_id=self.request.user.address['id'],
            global_nominal_account__nominal_account_number=reserved.VAT_CONTROL_ACCOUNT,
        )
        # Create a line for VAT
        results.append({
            'amount': tax_amount.quantize(Decimal('1.00'), rounding=ROUND_HALF_UP),
            'description': vat_description,
            'nominal_account_number': reserved.VAT_CONTROL_ACCOUNT,
            'quantity': 0,
            'unit_price': 0,
        })
        self.cleaned_data['debits'] = results

        # Make a credit for the Nominal Account specified by the `payment_method_id`
        self.cleaned_data['credit'] = {
            'amount': (gross_amount + tax_amount).quantize(Decimal('1.00'), rounding=ROUND_HALF_UP),
            'exchange_rate': 1,
            'quantity': 0,
            'unit_price': 0,
        }
        return None
