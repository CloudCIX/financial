"""
Management for VAT 3
This service displays aggregated data from the Nominal Ledger. It does not create VAT 3 records
"""

# stdlib
from decimal import Decimal
# libs
from cloudcix_rest.exceptions import Http400, Http404
from django.conf import settings
from django.db.models import Q, Sum
from django.db.models.functions import Coalesce
from rest_framework.request import Request
from rest_framework.response import Response
# local
from financial import reserved_accounts as reserved
from financial.api_view import FinancialAPIView as APIView
from financial.controllers.vat3 import VAT3ListController
from financial.models import NominalLedgerCredit, NominalLedgerDebit, TaxRate
from financial.utils import VIESCalculator


__all__ = [
    'VAT3Collection',
]


class VAT3Collection(APIView):
    """
    Handles methods regarding records on the Nominal Ledger that don't require an id to be specified, i.e. list
    """

    def get(self, request: Request) -> Response:
        """
        summary: Calculate all values required in a Revenue VAT3 form

        description: |
            Calculate the total vat on sales and purchases for a date period, and the total sales and purchases to other
            countries in the EU

        responses:
            200:
                description: A list of transaction totals in the format of a VAT3 form
            400: {}
        """
        tracer = settings.TRACER

        with tracer.start_span('retrieving_tax_rate', child_of=request.span):
            try:
                tax_rate = TaxRate.objects.get(
                    address_id=request.user.address['id'],
                    percent=Decimal('0'),
                    description__icontains='export',
                )
            except TaxRate.DoesNotExist:
                return Http404(error_code='financial_vat3_list_001')

        with tracer.start_span('validating_controller', child_of=request.span) as span:
            controller = VAT3ListController(data=request.GET, request=request, span=span)
            # By validating the controller we generate the filters
            if not controller.is_valid():
                return Http400(errors=controller.errors)

        with tracer.start_span('calculating_vat', child_of=request.span):
            cd = controller.cleaned_data
            # Get every ledger line that credits the VAT control account
            credits = NominalLedgerCredit.objects.filter(
                nominal_account_number=reserved.VAT_CONTROL_ACCOUNT,
                nominal_ledger__address_id=request.user.address['id'],
                nominal_ledger__transaction_date__range=(cd['start_date'], cd['end_date']),
            ).aggregate(
                sales=Coalesce(
                    Sum('amount', filter=Q(nominal_ledger__transaction_type_id__in=(11000, 11002, 11006))),
                    Decimal('0'),
                ),
                purchase_refunds=Coalesce(
                    Sum('amount', filter=Q(nominal_ledger__transaction_type_id__in=(10001, 10003, 10007))),
                    Decimal('0'),
                ),
            )

            # Get every ledger line that debits the VAT control account
            debits = NominalLedgerDebit.objects.filter(
                nominal_account_number=reserved.VAT_CONTROL_ACCOUNT,
                nominal_ledger__address_id=request.user.address['id'],
                nominal_ledger__transaction_date__range=(cd['start_date'], cd['end_date']),
            ).aggregate(
                purchases=Coalesce(
                    Sum('amount', filter=Q(nominal_ledger__transaction_type_id__in=(10000, 10002, 10006))),
                    Decimal('0'),
                ),
                sale_refunds=Coalesce(
                    Sum('amount', filter=Q(nominal_ledger__transaction_type_id__in=(11001, 11003, 11007))),
                    Decimal('0'),
                ),
            )

            vat = dict()
            # Calculate sales and purchases
            vat['sales'] = credits['sales'] - debits['sale_refunds']
            vat['sales'] = vat['sales'].quantize(Decimal('1.00'))

            vat['purchases'] = debits['purchases'] - credits['purchase_refunds']
            vat['purchases'] = vat['purchases'].quantize(Decimal('1.00'))

            vat['payable'] = vat['sales'] - vat['purchases']

        with tracer.start_span('calculating_eu_sales', child_of=request.span) as span:
            # Calculate the Sale Invoices - Sale Credit Notes
            with tracer.start_span('calculating_credit_notes', child_of=span):
                calculator = VIESCalculator(request, tax_rate.id)
                calculator.set_model(NominalLedgerDebit)
                calculator.update_filters(
                    nominal_ledger__transaction_type_id__in=(11001, 11003, 11007),
                    nominal_ledger__transaction_date__range=(cd['start_date'], cd['end_date']),
                )
                transaction_totals = calculator.get_transaction_totals()
                sale_refunds = sum([t.amount for t in transaction_totals])

            with tracer.start_span('calculating_sale_invoices', child_of=span):
                calculator.update_filters(nominal_ledger__transaction_type_id__in=(11000, 11002, 11006))
                calculator.set_model(NominalLedgerCredit)
                transaction_totals = calculator.get_transaction_totals()
                sales = sum([t.amount for t in transaction_totals])

            eu_sales = Decimal(sales - sale_refunds)
            eu_sales = eu_sales.quantize(Decimal('1.00'))

        with tracer.start_span('calculating_eu_purchases', child_of=request.span) as span:
            # Calculate the Purchase Invoices - Purchase Debit Notes
            with tracer.start_span('calculating_debit_notes', child_of=span):
                calculator.set_model(NominalLedgerCredit)
                calculator.update_filters(nominal_ledger__transaction_type_id__in=(10001, 10003, 10007))
                transaction_totals = calculator.get_transaction_totals()
                purchase_refunds = sum([t.amount for t in transaction_totals])

            with tracer.start_span('calculating_purchase_invoices', child_of=span):
                calculator.set_model(NominalLedgerDebit)
                calculator.update_filters(nominal_ledger__transaction_type_id__in=(10000, 10002, 10006))
                transaction_totals = calculator.get_transaction_totals()
                purchases = sum([t.amount for t in transaction_totals])

            eu_purchases = Decimal(purchases - purchase_refunds)
            eu_purchases = eu_purchases.quantize(Decimal('1.00'))

        with tracer.start_span('gathering_metadata', child_of=request.span):
            data = {
                'eu_purchases': str(eu_purchases),
                'eu_sales': str(eu_sales),
                'net_payable': str(vat['payable']),
                'vat_on_purchases': str(vat['purchases']),
                'vat_on_sales': str(vat['sales']),
            }

        return Response({'content': data})
