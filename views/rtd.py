"""
Management for Return of Trading Details
This service displays aggregated data from the Nominal Ledger. It does not create Return of Trading Details records
"""

# stdlib
from copy import copy
from decimal import Decimal
from operator import itemgetter
# libs
from cloudcix_rest.exceptions import Http400
from django.conf import settings
from django.db.models import Q, Sum
from django.db.models.functions import Coalesce
from rest_framework.request import Request
from rest_framework.response import Response
# local
from financial.eu_countries import eu_countries
from financial.api_view import FinancialAPIView as APIView
from financial.controllers.rtd import RTDListController
from financial.models import NominalAccountType, NominalLedgerCredit, NominalLedgerDebit, TaxRate
from financial.permissions.rtd import Permissions
from financial.serializers import RTDSerializer
from financial.utils import UK_LEFT_EU


IRELAND = 372

__all__ = [
    'RTDCollection',
]


class RTDCollection(APIView):
    """
    Handles methods regarding records on the Nominal Ledger that don't require an id to be specified, i.e. list
    """

    def get(self, request: Request) -> Response:
        """
        summary: Calculate all values for a Return of Trading Details (RTD) report

        description: |
            Calculate the total values excluding VAT of all Sales, EU Acquisitions, Purchases for resale, and
            Purchases not for resale, for a given year

        responses:
            200:
                description: |
                    A dictionary of transaction totals for all the headings in an RTD report, broken down by
                    Tax Rate
            400: {}
        """
        tracer = settings.TRACER

        with tracer.start_span('checking_permissions', child_of=request.span):
            err = Permissions.list(request)
            if err is not None:
                return err

        with tracer.start_span('validating_controller', child_of=request.span) as span:
            controller = RTDListController(data=request.GET, request=request, span=span)
            # By validating the controller we generate search filters
            if not controller.is_valid():
                return Http400(errors=controller.errors)

        with tracer.start_span('calculating_all_sales', child_of=request.span) as span:
            cd = controller.cleaned_data
            filters = {
                'tax_rate_id__isnull': False,
                'nominal_ledger__address_id': request.user.address['id'],
                'nominal_ledger__transaction_date__range': (cd['start_date'], cd['end_date']),
            }
            sale_accounts = NominalAccountType.objects.get(description__iexact='sales')

            # Calculate all sales. Figures should exclude VAT
            with tracer.start_span('calculating_sale_invoices', child_of=span):
                sales = NominalLedgerCredit.objects.filter(
                    nominal_account_number__range=(sale_accounts.min_account_number, sale_accounts.max_account_number),
                    nominal_ledger__transaction_type_id__in=(11000, 11002, 11006),
                    **filters,
                ).values(
                    'tax_rate_id',
                ).annotate(
                    total=Coalesce(Sum('amount'), Decimal('0')),
                )

            with tracer.start_span('calculating_credit_notes', child_of=span):
                sale_refunds = NominalLedgerDebit.objects.filter(
                    nominal_account_number__range=(sale_accounts.min_account_number, sale_accounts.max_account_number),
                    nominal_ledger__transaction_type_id__in=(11001, 11003, 11007),
                    **filters,
                ).values(
                    'tax_rate_id',
                ).annotate(
                    total=Coalesce(Sum('amount'), Decimal('0')),
                )

            sale_totals = dict()
            # Calculate the total Invoices less Credit Notes for each Tax Tate
            for item in sales:
                sale_totals[item['tax_rate_id']] = item['total']

            for item in sale_refunds:
                tax_id = item['tax_rate_id']
                if tax_id in sale_totals:
                    sale_totals[tax_id] -= item['total']
                else:
                    sale_totals[tax_id] = -1 * item['total']

        with tracer.start_span('calculating_EU_acquisitions', child_of=request.span) as span:
            eu_country_ids = copy(eu_countries)
            eu_country_ids.pop(IRELAND)
            eu_country_ids = list(eu_country_ids.keys())

            with tracer.start_span('calculating_purchase_invoices', child_of=span):
                # Get all purchase invoices from EU countries excluding Ireland
                purchases = NominalLedgerDebit.objects.filter(
                    Q(nominal_account_number__range=(1, 999)) | Q(nominal_account_number__range=(5000, 7999)),
                    nominal_ledger__transaction_type_id__in=(10000, 10002, 10006),
                    nominal_ledger__country_id_bill_to__in=eu_country_ids,
                    **filters,
                ).exclude(
                    Q(nominal_ledger__transaction_date__gt=UK_LEFT_EU) & Q(nominal_ledger__country_id_bill_to=826),
                ).values(
                    'tax_rate_id',
                ).annotate(
                    total=Coalesce(Sum('amount'), Decimal('0')),
                )

            with tracer.start_span('calculating_debit_notes', child_of=span):
                # Get all debit notes to EU countries excluding Ireland
                purchase_refunds = NominalLedgerCredit.objects.filter(
                    Q(nominal_account_number__range=(1, 999)) | Q(nominal_account_number__range=(5000, 7999)),
                    nominal_ledger__transaction_type_id__in=(10001, 10003, 10007),
                    nominal_ledger__country_id_bill_to__in=eu_country_ids,
                    **filters,
                ).exclude(
                    Q(nominal_ledger__transaction_date__gt=UK_LEFT_EU) & Q(nominal_ledger__country_id_bill_to=826),
                ).values(
                    'tax_rate_id',
                ).annotate(
                    total=Coalesce(Sum('amount'), Decimal('0')),
                )

            eu_purchase_totals = dict()
            # Calculate the total Invoices less Debit Notes for each Tax Tate
            for item in purchases:
                eu_purchase_totals[item['tax_rate_id']] = item['total']

            for item in purchase_refunds:
                tax_id = item['tax_rate_id']
                if tax_id in eu_purchase_totals:
                    eu_purchase_totals[tax_id] -= item['total']
                else:
                    eu_purchase_totals[tax_id] = -1 * item['total']

        with tracer.start_span('calculating_resale_purchases', child_of=request.span) as span:
            purchase_account = NominalAccountType.objects.get(description__iexact='purchases')
            with tracer.start_span('calculating_resale_invoices', child_of=span):
                resale = NominalLedgerDebit.objects.filter(
                    nominal_account_number__range=(
                        purchase_account.min_account_number,
                        purchase_account.max_account_number,
                    ),
                    nominal_ledger__transaction_type_id__in=(10000, 10002, 10006),
                    **filters,
                ).values(
                    'tax_rate_id',
                ).annotate(
                    total=Coalesce(Sum('amount'), Decimal('0')),
                )

            with tracer.start_span('calculating_resale_debit_notes', child_of=span):
                resale_refunds = NominalLedgerCredit.objects.filter(
                    nominal_account_number__range=(
                        purchase_account.min_account_number,
                        purchase_account.max_account_number,
                    ),
                    nominal_ledger__transaction_type_id__in=(10001, 10003, 10007),
                    **filters,
                ).values(
                    'tax_rate_id',
                ).annotate(
                    total=Coalesce(Sum('amount'), Decimal('0')),
                )

            resale_purchase_totals = dict()
            # Calculate the total Invoices less Debit Notes for each Tax Tate
            for item in resale:
                resale_purchase_totals[item['tax_rate_id']] = item['total']

            for item in resale_refunds:
                tax_id = item['tax_rate_id']
                if tax_id in resale_purchase_totals:
                    resale_purchase_totals[tax_id] -= item['total']
                else:
                    resale_purchase_totals[tax_id] = -1 * item['total']

        with tracer.start_span('calculating_non_resale_purchases', child_of=request.span) as span:
            with tracer.start_span('calculating_non_resale_invoices', child_of=span):
                non_resale = NominalLedgerDebit.objects.filter(
                    Q(nominal_account_number__range=(1, 999)) | Q(nominal_account_number__range=(6000, 7999)),
                    nominal_ledger__transaction_type_id__in=(10000, 10002, 10006),
                    **filters,
                ).values(
                    'tax_rate_id',
                ).annotate(
                    total=Coalesce(Sum('amount'), Decimal('0')),
                )

            with tracer.start_span('calculating_non_resale_debit_notes', child_of=span):
                non_resale_refunds = NominalLedgerCredit.objects.filter(
                    Q(nominal_account_number__range=(1, 999)) | Q(nominal_account_number__range=(6000, 7999)),
                    nominal_ledger__transaction_type_id__in=(10001, 10003, 10007),
                    **filters,
                ).values(
                    'tax_rate_id',
                ).annotate(
                    total=Coalesce(Sum('amount'), Decimal('0')),
                )

            non_resale_purchase_totals = dict()
            # Calculate the total Invoices less Debit Notes for each Tax Tate
            for item in non_resale:
                non_resale_purchase_totals[item['tax_rate_id']] = item['total']

            for item in non_resale_refunds:
                tax_id = item['tax_rate_id']
                if tax_id in non_resale_purchase_totals:
                    non_resale_purchase_totals[tax_id] -= item['total']
                else:
                    non_resale_purchase_totals[tax_id] = -1 * item['total']

        with tracer.start_span('gathering_tax_rates', child_of=request.span):
            # The percentage on a Tax Rate could change from year to year so get Tax Percentages from debit/credit lines
            tax_percents = list(NominalLedgerCredit.objects.filter(**filters).values('tax_rate_id', 'tax_percent'))
            tax_percents.extend(list(NominalLedgerDebit.objects.filter(**filters).values('tax_rate_id', 'tax_percent')))

            # Get all the Tax Rates in the User's Address
            rates = TaxRate.objects.filter(address_id=request.user.address['id']).values('id', 'description')
            rates = {r['id']: r for r in rates}
            for tax_rate_id, rate in rates.items():
                # For each Tax Rate, find its percent value from the list of percentages
                for item in tax_percents:
                    if tax_rate_id == item['tax_rate_id']:
                        rate['percent'] = item['tax_percent']
                        break

            # Create the data structure that will be returned
            total_sales = Decimal('0')
            sales = list()
            for tax_id, total in sale_totals.items():
                sales.append({
                    'total': total,
                    **rates[tax_id],
                })
                total_sales += total

            total_eu_purchases = Decimal('0')
            eu_purchases = list()
            for tax_id, total in eu_purchase_totals.items():
                eu_purchases.append({
                    'total': total,
                    **rates[tax_id],
                })
                total_eu_purchases += total

            total_resale_purchases = Decimal('0')
            resale_purchases = list()
            for tax_id, total in resale_purchase_totals.items():
                resale_purchases.append({
                    'total': total,
                    **rates[tax_id],
                })
                total_resale_purchases += total

            total_non_resale_purchases = Decimal('0')
            non_resale_purchases = list()
            for tax_id, total in non_resale_purchase_totals.items():
                non_resale_purchases.append({
                    'total': total,
                    **rates[tax_id],
                })
                total_non_resale_purchases += total

            # Order the results by Tax Percent and Tax Description
            sales.sort(key=itemgetter('percent', 'description'))
            eu_purchases.sort(key=itemgetter('percent', 'description'))
            resale_purchases.sort(key=itemgetter('percent', 'description'))
            non_resale_purchases.sort(key=itemgetter('percent', 'description'))

        with tracer.start_span('gathering_metadata', child_of=request.span):
            meta = {
                'total_sales': str(total_sales.quantize(Decimal('1.0000'))),
                'total_eu_purchases': str(total_eu_purchases.quantize(Decimal('1.0000'))),
                'total_resale_purchases': str(total_resale_purchases.quantize(Decimal('1.0000'))),
                'total_non_resale_purchases': str(total_non_resale_purchases.quantize(Decimal('1.0000'))),
            }

        with tracer.start_span('serializing_data', child_of=request.span):
            data = {
                'sales': sales,
                'eu_purchases': eu_purchases,
                'resale_purchases': resale_purchases,
                'non_resale_purchases': non_resale_purchases,
            }
            data = RTDSerializer(instance=data).data

        return Response({'content': data, '_metadata': meta})
