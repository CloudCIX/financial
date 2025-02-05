# stdlib
from collections import deque
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from typing import cast, Deque, Dict, List, Optional, Set, Union
# libs
from cloudcix.api.membership import Membership
from cloudcix_rest.controllers import ControllerBase
# local
from financial import reserved_accounts as reserved
from financial.controllers.transaction_mixin import FinancialException, TransactionMixin
from financial.models import AddressNominalAccount, NominalLedger, NominalLedgerDebit, TaxRate


__all__ = [
    'CashSaleReceiptCreateController',
    'CashSaleReceiptUpdateController',
]

CREDIT = Dict[str, Union[int, str, Decimal]]
DEBIT = CREDIT
VALID_ACCOUNT_RANGE = range(1000, 3000)


class CashSaleReceiptCreateController(ControllerBase, TransactionMixin):
    """
    Validate User data to create a new Nominal Ledger record for a Cash Sale Receipt transaction
    """

    class Meta(ControllerBase.Meta):
        """
        Override some of the ControllerBase.Meta fields to make them more specific for this Controller
        """
        model = NominalLedger
        validation_order = (
            'address1_bill_to',
            'address1_deliver_to',
            'address2_bill_to',
            'address2_deliver_to',
            'address3_bill_to',
            'address3_deliver_to',
            'city_bill_to',
            'city_deliver_to',
            'contra_contact',
            'country_id_deliver_to',
            'external_reference',
            'name_bill_to',
            'name_deliver_to',
            'narrative',
            'postcode_bill_to',
            'postcode_deliver_to',
            'subdivision_id_deliver_to',
            'transaction_date',
            'lines',
            'payment_method_id',
            'report_template_id',
        )

    def validate_address1_bill_to(self, address: Optional[str]) -> Optional[str]:
        """
        description: The first line of the geographic address to bill the Cash Sale Receipt to
        type: string
        required: false
        """
        try:
            address = self._validate_address1_bill_to(address, 'financial_cash_sale_receipt_create_101')
        except FinancialException as e:
            return e.args[0]
        self.cleaned_data['address1_bill_to'] = address
        return None

    def validate_address1_deliver_to(self, address: Optional[str]) -> Optional[str]:
        """
        description: The first line of the geographic address to deliver the items on the Cash Sale Receipt to
        type: string
        required: false
        """
        try:
            address = self._validate_address1_deliver_to(address, 'financial_cash_sale_receipt_create_102')
        except FinancialException as e:
            return e.args[0]
        self.cleaned_data['address1_deliver_to'] = address
        return None

    def validate_address2_bill_to(self, address: Optional[str]) -> Optional[str]:
        """
        description: The second line of the geographic address to bill the Cash Sale Receipt to
        type: string
        required: false
        """
        try:
            address = self._validate_address2_bill_to(address, 'financial_cash_sale_receipt_create_103')
        except FinancialException as e:
            return e.args[0]
        self.cleaned_data['address2_bill_to'] = address
        return None

    def validate_address2_deliver_to(self, address: Optional[str]) -> Optional[str]:
        """
        description: The second line of the geographic address to deliver the items on the Cash Sale Receipt to
        type: string
        required: false
        """
        try:
            address = self._validate_address2_deliver_to(address, 'financial_cash_sale_receipt_create_104')
        except FinancialException as e:
            return e.args[0]
        self.cleaned_data['address2_deliver_to'] = address
        return None

    def validate_address3_bill_to(self, address: Optional[str]) -> Optional[str]:
        """
        description: The third line of the geographic address to bill the Cash Sale Receipt to
        type: string
        required: false
        """
        try:
            address = self._validate_address3_bill_to(address, 'financial_cash_sale_receipt_create_105')
        except FinancialException as e:
            return e.args[0]
        self.cleaned_data['address3_bill_to'] = address
        return None

    def validate_address3_deliver_to(self, address: Optional[str]) -> Optional[str]:
        """
        description: The third line of the geographic address to deliver the items on the Cash Sale Receipt to
        type: string
        required: false
        """
        try:
            address = self._validate_address3_deliver_to(address, 'financial_cash_sale_receipt_create_106')
        except FinancialException as e:
            return e.args[0]
        self.cleaned_data['address3_deliver_to'] = address
        return None

    def validate_city_bill_to(self, city: Optional[str]) -> Optional[str]:
        """
        description: The city where the company on the Cash Sale Receipt is situated
        type: string
        required: false
        """
        try:
            city = self._validate_city_bill_to(city, 'financial_cash_sale_receipt_create_107')
        except FinancialException as e:
            return e.args[0]
        self.cleaned_data['city_bill_to'] = city
        return None

    def validate_city_deliver_to(self, city: Optional[str]) -> Optional[str]:
        """
        description: The city where the items on the Cash Sale Receipt must be delivered to
        type: string
        required: false
        """
        try:
            city = self._validate_city_deliver_to(city, 'financial_cash_sale_receipt_create_108')
        except FinancialException as e:
            return e.args[0]
        self.cleaned_data['city_deliver_to'] = city
        return None

    def validate_contra_contact(self, contra_contact: Optional[str]) -> Optional[str]:
        """
        description: The name of the person who requested the Cash Sale Receipt
        type: string
        required: false
        """
        try:
            contra_contact = self._validate_contra_contact(contra_contact, 'financial_cash_sale_receipt_create_109')
        except FinancialException as e:
            return e.args[0]
        self.cleaned_data['contra_contact'] = contra_contact
        return None

    def validate_country_id_deliver_to(self, country_id: Optional[int]) -> Optional[str]:
        """
        description: The id of the country to deliver the items on the Cash Sale Invoice to
        type: integer
        required: false
        """
        try:
            country_id = self._validate_country_id(
                country_id,
                'financial_cash_sale_receipt_create_110',
                'financial_cash_sale_receipt_create_111',
            )
        except FinancialException as e:
            return e.args[0]

        self.cleaned_data['country_id_deliver_to'] = country_id
        return None

    def validate_external_reference(self, reference: Optional[str]) -> Optional[str]:
        """
        description: The identifier for this Cash Sale Receipt in the Contra Address' referencing scheme
        type: string
        required: false
        """
        try:
            reference = self._validate_external_reference(reference, 'financial_cash_sale_receipt_create_112')
        except FinancialException as e:
            return e.args[0]
        self.cleaned_data['external_reference'] = reference
        return None

    def validate_name_bill_to(self, name: Optional[str]) -> Optional[str]:
        """
        description: The name of the company to bill the Cash Sale Receipt to
        type: string
        required: false
        """
        try:
            name = self._validate_name_bill_to(name, 'financial_cash_sale_receipt_create_113')
        except FinancialException as e:
            return e.args[0]
        self.cleaned_data['name_bill_to'] = name
        return None

    def validate_name_deliver_to(self, name: Optional[str]) -> Optional[str]:
        """
        description: The name of the company to deliver the items on the Cash Sale Receipt to
        type: string
        required: false
        """
        try:
            name = self._validate_name_deliver_to(name, 'financial_cash_sale_receipt_create_114')
        except FinancialException as e:
            return e.args[0]
        self.cleaned_data['name_deliver_to'] = name
        return None

    def validate_narrative(self, narrative: Optional[str]) -> Optional[str]:
        """
        description: A summary of the Sale Receipt and its items
        type: string
        required: false
        """
        try:
            narrative = self._validate_narrative(narrative, 'financial_cash_sale_receipt_create_115')
        except FinancialException as e:
            return e.args[0]
        self.cleaned_data['narrative'] = narrative
        return None

    def validate_postcode_bill_to(self, postcode: Optional[str]) -> Optional[str]:
        """
        description: The postcode of the company to bill the Cash Sale Receipt to
        type: string
        required: false
        """
        try:
            postcode = self._validate_postcode_bill_to(postcode, 'financial_cash_sale_receipt_create_116')
        except FinancialException as e:
            return e.args[0]
        self.cleaned_data['postcode_bill_to'] = postcode
        return None

    def validate_postcode_deliver_to(self, postcode: Optional[str]) -> Optional[str]:
        """
        description: The postcode of the company to deliver the items on the Cash Sale Receipt to
        type: string
        required: false
        """
        try:
            postcode = self._validate_postcode_deliver_to(postcode, 'financial_cash_sale_receipt_create_117')
        except FinancialException as e:
            return e.args[0]
        self.cleaned_data['postcode_deliver_to'] = postcode
        return None

    def validate_subdivision_id_deliver_to(self, subdivision_id: Optional[int]) -> Optional[str]:
        """
        description: The subdivision to deliver the items on the Cash Sale Receipt to
        type: string
        required: false
        """
        try:
            subdivision_id = self._validate_subdivision_id(
                subdivision_id,
                'financial_cash_sale_receipt_create_118',
                'financial_cash_sale_receipt_create_119',
            )
        except FinancialException as e:
            return e.args[0]
        self.cleaned_data['subdivision_id_deliver_to'] = subdivision_id
        return None

    def validate_transaction_date(self, date: Optional[str]) -> Optional[str]:
        """
        description: The date that the Cash Sale Receipt was created
        type: string
        """
        try:
            transaction_date = self._validate_transaction_date(
                date,
                'financial_cash_sale_receipt_create_120',
                'financial_cash_sale_receipt_create_121',
            )
        except FinancialException as e:
            return e.args[0]
        self.cleaned_data['transaction_date'] = transaction_date
        return None

    def validate_lines(self, lines: Optional[List[CREDIT]]):
        """
        description: A collection of the amounts to credit from each Nominal Account for this Cash Sale Receipt
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
            return 'financial_cash_sale_receipt_create_122'

        account_numbers: Set[int] = set()
        tax_rate_ids: Set[int] = set()
        for line in lines:
            if not isinstance(line, dict):
                return 'financial_cash_sale_receipt_create_123'

            try:
                description = cast(str, line['description'])
            except KeyError:
                return 'financial_cash_sale_receipt_create_124'
            if len(description) > NominalLedgerDebit._meta.get_field('description').max_length:
                return 'financial_cash_sale_receipt_create_125'

            try:
                line['exchange_rate'] = Decimal(str(line.get('exchange_rate', 1)))
            except InvalidOperation:
                return 'financial_cash_sale_receipt_create_126'

            try:
                number = int(cast(int, line['number']))
                if number not in range(0, 8000):
                    return 'financial_cash_sale_receipt_create_127'
                line['number'] = number
                account_numbers.add(number)
            except (KeyError, TypeError, ValueError):
                return 'financial_cash_sale_receipt_create_128'

            try:
                line['quantity'] = Decimal(str(line['quantity']))
            except (InvalidOperation, KeyError):
                return 'financial_cash_sale_receipt_create_129'

            try:
                tax_rate_id = int(cast(int, line['tax_rate_id']))
                line['tax_rate_id'] = tax_rate_id
                tax_rate_ids.add(tax_rate_id)
            except (KeyError, TypeError, ValueError):
                return 'financial_cash_sale_receipt_create_130'

            try:
                line['unit_price'] = Decimal(str(line['unit_price']))
            except (InvalidOperation, KeyError):
                return 'financial_cash_sale_receipt_create_131'

        # Make sure all the Nominal Accounts exist
        accounts = AddressNominalAccount.objects.filter(
            address_id=self.request.user.address['id'],
            global_nominal_account__nominal_account_number__in=account_numbers,
        )
        if len(accounts) != len(account_numbers):
            return 'financial_cash_sale_receipt_create_132'
        for a in accounts:
            if not a.global_nominal_account.valid_sales_account and \
                    a.global_nominal_account.nominal_account_number != reserved.VAT_CONTROL_ACCOUNT:
                return 'financial_cash_sale_receipt_create_133'

        # Make sure all the Tax Rates exist
        tax_rates = TaxRate.objects.filter(
            address_id=self.request.user.address['id'],
            id__in=tax_rate_ids,
        )
        if len(tax_rates) != len(tax_rate_ids):
            return 'financial_cash_sale_receipt_create_134'
        # Put the Tax Rate records in a dictionary for easy access
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

            # Calculate amounts and tax in the User's base currency
            exchange_rate = cast(Decimal, line['exchange_rate'])
            gross_amount += amount * exchange_rate

            # Validate the tax on each item
            tax_rate = tax_rates[line['tax_rate_id']]
            tax_percent = cast(Decimal, tax_rate.percent)
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
            return 'financial_cash_sale_receipt_create_135'

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
            'amount': (tax_amount).quantize(rounding_figure, rounding=ROUND_HALF_UP),
            'description': vat_description,
            'exchange_rate': 1,
            'nominal_account_number': reserved.VAT_CONTROL_ACCOUNT,
            'quantity': 0,
            'unit_price': 0,
        })
        self.cleaned_data['credits'] = results
        self.cleaned_data['debit'] = {
            'amount': (gross_amount + tax_amount).quantize(rounding_figure, rounding=ROUND_HALF_UP),
            'exchange_rate': 1,
            'quantity': 0,
            'unit_price': 0,
        }
        return None

    def validate_payment_method_id(self, payment_method_id: Optional[int]) -> Optional[str]:
        """
        description: |
            How the requesting User will receive payment for the Sale Receipt. This will determine what Nominal Account
            will be debited by checking the Nominal Contra records
        type: integer
        """
        try:
            address_account = self._validate_payment_method_id(
                payment_method_id,
                11006,
                'financial_cash_sale_receipt_create_136',
                'financial_cash_sale_receipt_create_137',
                'financial_cash_sale_receipt_create_138',
                'financial_cash_sale_receipt_create_139',
                'financial_cash_sale_receipt_create_140',
            )
        except FinancialException as e:
            return e.args[0]

        self.cleaned_data['address_account'] = address_account
        return None

    def validate_report_template_id(self, report_template_id: Optional[int]) -> Optional[str]:
        """
        description: The id of the Report Template to use when printing the Cash Sale Receipt
        type: integer
        """
        try:
            report_template_id = self._validate_report_template_id(
                report_template_id,
                11006,
                'financial_cash_sale_receipt_create_141',
                'financial_cash_sale_receipt_create_142',
                'financial_cash_sale_receipt_create_143',
            )
        except FinancialException as e:
            return e.args[0]
        self.cleaned_data['report_template_id'] = report_template_id
        return None


class CashSaleReceiptUpdateController(ControllerBase, TransactionMixin):
    """
    Validate User data to create a new Nominal Ledger record for a Cash Sale Receipt transaction
    """

    class Meta(ControllerBase.Meta):
        """
        Override some of the ControllerBase.Meta fields to make them more specific for this Controller
        """
        model = NominalLedger
        validation_order = (
            'address1_bill_to',
            'address1_deliver_to',
            'address2_bill_to',
            'address2_deliver_to',
            'address3_bill_to',
            'address3_deliver_to',
            'city_bill_to',
            'city_deliver_to',
            'contra_contact',
            'country_id_deliver_to',
            'external_reference',
            'name_bill_to',
            'name_deliver_to',
            'narrative',
            'postcode_bill_to',
            'postcode_deliver_to',
            'subdivision_id_deliver_to',
        )

    def validate_address1_bill_to(self, address: Optional[str]) -> Optional[str]:
        """
        description: The first line of the geographic address to bill the Cash Sale Receipt to
        type: string
        required: false
        """
        try:
            address = self._validate_address1_bill_to(address, 'financial_cash_sale_receipt_update_101')
        except FinancialException as e:
            return e.args[0]
        self.cleaned_data['address1_bill_to'] = address
        return None

    def validate_address1_deliver_to(self, address: Optional[str]) -> Optional[str]:
        """
        description: The first line of the geographic address to deliver the items on the Cash Sale Receipt to
        type: string
        required: false
        """
        try:
            address = self._validate_address1_deliver_to(address, 'financial_cash_sale_receipt_update_102')
        except FinancialException as e:
            return e.args[0]
        self.cleaned_data['address1_deliver_to'] = address
        return None

    def validate_address2_bill_to(self, address: Optional[str]) -> Optional[str]:
        """
        description: The second line of the geographic address to bill the Cash Sale Receipt to
        type: string
        required: false
        """
        try:
            address = self._validate_address2_bill_to(address, 'financial_cash_sale_receipt_update_103')
        except FinancialException as e:
            return e.args[0]
        self.cleaned_data['address2_bill_to'] = address
        return None

    def validate_address2_deliver_to(self, address: Optional[str]) -> Optional[str]:
        """
        description: The second line of the geographic address to deliver the items on the Cash Sale Receipt to
        type: string
        required: false
        """
        try:
            address = self._validate_address2_deliver_to(address, 'financial_cash_sale_receipt_update_104')
        except FinancialException as e:
            return e.args[0]
        self.cleaned_data['address2_deliver_to'] = address
        return None

    def validate_address3_bill_to(self, address: Optional[str]) -> Optional[str]:
        """
        description: The third line of the geographic address to bill the Cash Sale Receipt to
        type: string
        required: false
        """
        try:
            address = self._validate_address3_bill_to(address, 'financial_cash_sale_receipt_update_105')
        except FinancialException as e:
            return e.args[0]
        self.cleaned_data['address3_bill_to'] = address
        return None

    def validate_address3_deliver_to(self, address: Optional[str]) -> Optional[str]:
        """
        description: The third line of the geographic address to deliver the items on the Cash Sale Receipt to
        type: string
        required: false
        """
        try:
            address = self._validate_address3_deliver_to(address, 'financial_cash_sale_receipt_update_106')
        except FinancialException as e:
            return e.args[0]
        self.cleaned_data['address3_deliver_to'] = address
        return None

    def validate_city_bill_to(self, city: Optional[str]) -> Optional[str]:
        """
        description: The city where the company on the Cash Sale Receipt is situated
        type: string
        required: false
        """
        try:
            city = self._validate_address3_deliver_to(city, 'financial_cash_sale_receipt_update_107')
        except FinancialException as e:
            return e.args[0]
        self.cleaned_data['city_bill_to'] = city
        return None

    def validate_city_deliver_to(self, city: Optional[str]) -> Optional[str]:
        """
        description: The city where the items on the Cash Sale Receipt must be delivered to
        type: string
        required: false
        """
        try:
            city = self._validate_address3_deliver_to(city, 'financial_cash_sale_receipt_update_108')
        except FinancialException as e:
            return e.args[0]
        self.cleaned_data['city_deliver_to'] = city
        return None

    def validate_contra_contact(self, contra_contact: Optional[str]) -> Optional[str]:
        """
        description: The name of the person who requested the Cash Sale Receipt
        type: string
        required: false
        """
        try:
            contra_contact = self._validate_contra_contact(contra_contact, 'financial_cash_sale_receipt_update_109')
        except FinancialException as e:
            return e.args[0]
        self.cleaned_data['contra_contact'] = contra_contact
        return None

    def validate_country_id_deliver_to(self, country_id: Optional[int]) -> Optional[str]:
        """
        description: The id of the country to deliver the items on the Cash Sale Invoice to
        type: integer
        required: false
        """
        try:
            country_id = self._validate_country_id(
                country_id,
                'financial_cash_sale_receipt_update_110',
                'financial_cash_sale_receipt_update_111',
            )
        except FinancialException as e:
            return e.args[0]

        self.cleaned_data['country_id_deliver_to'] = country_id
        return None

    def validate_external_reference(self, reference: Optional[str]) -> Optional[str]:
        """
        description: The identifier for this Cash Sale Receipt in the Contra Address' referencing scheme
        type: string
        required: false
        """
        try:
            reference = self._validate_external_reference(reference, 'financial_cash_sale_receipt_update_112')
        except FinancialException as e:
            return e.args[0]
        self.cleaned_data['external_reference'] = reference
        return None

    def validate_name_bill_to(self, name: Optional[str]) -> Optional[str]:
        """
        description: The name of the company to bill the Cash Sale Receipt to
        type: string
        required: false
        """
        try:
            name = self._validate_name_bill_to(name, 'financial_cash_sale_receipt_update_113')
        except FinancialException as e:
            return e.args[0]
        self.cleaned_data['name_bill_to'] = name
        return None

    def validate_name_deliver_to(self, name: Optional[str]) -> Optional[str]:
        """
        description: The name of the company to deliver the items on the Cash Sale Receipt to
        type: string
        required: false
        """
        try:
            name = self._validate_name_bill_to(name, 'financial_cash_sale_receipt_update_114')
        except FinancialException as e:
            return e.args[0]
        self.cleaned_data['name_deliver_to'] = name
        return None

    def validate_narrative(self, narrative: Optional[str]) -> Optional[str]:
        """
        description: A summary of the Sale Receipt and its items
        type: string
        required: false
        """
        try:
            narrative = self._validate_narrative(narrative, 'financial_cash_sale_receipt_update_115')
        except FinancialException as e:
            return e.args[0]
        self.cleaned_data['narrative'] = narrative
        return None

    def validate_postcode_bill_to(self, postcode: Optional[str]) -> Optional[str]:
        """
        description: The postcode of the company to bill the Cash Sale Receipt to
        type: string
        required: false
        """
        try:
            postcode = self._validate_postcode_bill_to(postcode, 'financial_cash_sale_receipt_update_116')
        except FinancialException as e:
            return e.args[0]
        self.cleaned_data['postcode_bill_to'] = postcode
        return None

    def validate_postcode_deliver_to(self, postcode: Optional[str]) -> Optional[str]:
        """
        description: The postcode of the company to deliver the items on the Cash Sale Receipt to
        type: string
        required: false
        """
        try:
            postcode = self._validate_postcode_deliver_to(postcode, 'financial_cash_sale_receipt_update_117')
        except FinancialException as e:
            return e.args[0]
        self.cleaned_data['postcode_deliver_to'] = postcode
        return None

    def validate_subdivision_id_deliver_to(self, subdivision_id: Optional[int]) -> Optional[str]:
        """
        description: The subdivision to deliver the items on the Cash Sale Receipt to
        type: string
        required: false
        """
        if subdivision_id is None:
            return None

        try:
            subdivision_id = int(cast(int, subdivision_id))
        except (TypeError, ValueError):
            return 'financial_cash_sale_receipt_update_118'

        # A subdivision is only valid if a country is also specified
        if 'country_id_deliver_to' in self._errors:
            # Error validating the country id
            return None
        else:
            country_id = self.cleaned_data.get('country_id_deliver_to', self._instance.country_id_deliver_to)
            if country_id is None:
                return 'financial_cash_sale_receipt_update_119'

        response = Membership.subdivision.read(
            token=self.request.user.token,
            pk=subdivision_id,
            country_id=country_id,
            span=self.span,
        )
        if response.status_code != 200:
            return 'financial_cash_sale_receipt_update_120'

        self.cleaned_data['subdivision_id_deliver_to'] = subdivision_id
        return None
