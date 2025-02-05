"""
Management for the VIES Sales
This service displays aggregated data from the Nominal Ledger. It does not create VIES records
"""

# stdlib
from collections import deque
from decimal import Decimal
from operator import attrgetter
from typing import Deque
# libs
from cloudcix_rest.exceptions import Http400, Http404
from django.conf import settings
from django.core.exceptions import ValidationError
from rest_framework.request import Request
from rest_framework.response import Response
# local
from financial.api_view import FinancialAPIView as APIView
from financial.controllers.vies import VIESListController
from financial.eu_countries import eu_countries
from financial.models import NominalLedgerCredit, NominalLedgerDebit, TaxRate
from financial.serializers.vies import VIESSerializer
from financial.utils import VIESCalculator


__all__ = [
    'VIESSalesCollection',
]


class VIESSalesCollection(APIView):
    """
    Handles methods regarding records on the Nominal Ledger that don't require an id to be specified, i.e. list
    """

    serializer_class = VIESSerializer

    def get(self, request: Request) -> Response:
        """
        summary: Calculate the value of goods sold to other EU Countries at 0% VAT

        description: |
            Calculate the net value of goods sold by the requesting User's Address to Addresses in other EU countries
            at 0% VAT. Returns nothing if the requesting User's Address is not in the EU

        responses:
            200:
                description: A list of transaction totals grouped by Contra Address
            400: {}
        """
        tracer = settings.TRACER

        with tracer.start_span('check_country_id', child_of=request.span):
            if request.user.address['country_id'] not in eu_countries:
                return Response({'content': list()})

        with tracer.start_span('retrieve_export_tax_rate', child_of=request.span):
            try:
                tax_rate = TaxRate.objects.get(
                    address_id=request.user.address['id'],
                    percent=Decimal('0'),
                    description__icontains='export',
                )
            except TaxRate.DoesNotExist:
                return Http404(error_code='financial_vies_sales_list_001')

        with tracer.start_span('validating_controller', child_of=request.span) as span:
            controller = VIESListController(data=request.GET, request=request, span=span)
            # By validating the controller we generate the search filters
            controller.is_valid()

        with tracer.start_span('get_objects', child_of=request.span) as span:

            with tracer.start_span('get_credits', child_of=span):
                # Get the credits that were created from invoices
                calculator = VIESCalculator(request, tax_rate.id)
                calculator.set_model(NominalLedgerCredit)
                calculator.update_filters(
                    nominal_ledger__transaction_type_id__in=(11000, 11002),
                    **controller.cleaned_data['search'],
                )
                try:
                    credits = calculator.get_transaction_totals()
                except (ValueError, ValidationError):
                    return Http400(error_code='financial_vies_sales_list_002')

            with tracer.start_span('get_debits', child_of=span):
                # Get the debits that were created from credit notes. We're not introducing any new filters that can
                # cause errors, so if the credit filter passed, we don't need a try/except here
                calculator.set_model(NominalLedgerDebit)
                calculator.update_filters(nominal_ledger__transaction_type_id__in=(11001, 11003))
                debits = calculator.get_transaction_totals()

        with tracer.start_span('aggregating_results', child_of=request.span):
            results: Deque = deque()
            for c in credits:
                for d in debits:
                    if not d.used and c.address_id == d.address_id:
                        c.amount -= d.amount
                        d.used = True
                results.append(c)

            for d in debits:
                if not d.used:
                    d.amount = d.amount * -1
                    results.append(d)

            objs = sorted(results, key=attrgetter(controller.cleaned_data['order']))

        with tracer.start_span('serializing_data', child_of=request.span) as span:
            span.set_tag('num_objects', len(objs))
            data = VIESSerializer(instance=objs, many=True).data

        return Response({'content': data})
