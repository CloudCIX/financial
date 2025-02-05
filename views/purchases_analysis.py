"""
Management for the Sales Analysis service
This view presents aggregated data from the Nominal Ledger
"""

# stdlib
from decimal import Decimal
from operator import itemgetter
# libs
from cloudcix_rest.exceptions import Http400
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db.models import Q, Sum
from django.db.models.functions import Coalesce
from rest_framework.request import Request
from rest_framework.response import Response
# local
from financial import reserved_accounts as reserved
from financial.api_view import FinancialAPIView as APIView
from financial.controllers.purchases_analysis import PurchasesAnalysisListController
from financial.models import NominalLedger
from financial.serializers.purchases_analysis import PurchasesAnalysisSerializer


__all__ = [
    'PurchasesAnalysisCollection',
]


class PurchasesAnalysisCollection(APIView):
    """
    Handles methods regarding the Nominal Ledger that don't require an id to be specified i.e. list
    """

    def get(self, request: Request) -> Response:
        """
        summary: Get the total amounts purchased from each supplier Address, optionally filtering by Territory

        description: |
            Calculate the total amount purchased from Addresses that are marked as suppliers. Can optionally filter
            Addresses by their Territory The totals are calculated as the Purchase Invoices less the Debit Notes

        responses:
            200:
                description: A list of Addresses with the total amount purchased each one
            400: {}
        """
        tracer = settings.TRACER

        with tracer.start_span('validating_controller', child_of=request.span) as span:
            controller = PurchasesAnalysisListController(data=request.GET, request=request, span=span)
            # By validating the controller we generate the filters
            controller.is_valid()

        with tracer.start_span('get_objects', child_of=request.span) as span:
            with tracer.start_span('get_debits', child_of=span):
                cd = controller.cleaned_data
                try:
                    # Calculate all purchases from invoices. Search through the debit lines on the invoices as they
                    # will show how much of the invoice was VAT
                    purchases = NominalLedger.objects.filter(
                        address_id=request.user.address['id'],
                        transaction_type_id__in=(10000, 10002),
                        **cd['search'],
                    ).values(
                        'contra_address_id',
                    ).annotate(
                        total_ex_vat=Coalesce(Sum(
                            'debits__amount',
                            # Negate the Q object filter
                            filter=~Q(debits__nominal_account_number=reserved.VAT_CONTROL_ACCOUNT),
                        ), Decimal('0')),
                        vat=Coalesce(Sum(
                            'debits__amount',
                            filter=Q(debits__nominal_account_number=reserved.VAT_CONTROL_ACCOUNT),
                        ), Decimal('0')),
                    )
                except (ValueError, ValidationError):
                    return Http400(error_code='financial_purchases_analysis_list_001')

            with tracer.start_span('get_credits', child_of=span):
                # Calculate the amounts lost from debit notes. Search through the credit lines on the debit notes as
                # they will show how much of the transaction was vat
                debit_notes = NominalLedger.objects.filter(
                    address_id=request.user.address['id'],
                    transaction_type_id__in=(10001, 10003),
                    **cd['search'],
                ).values(
                    'contra_address_id',
                ).annotate(
                    total_ex_vat=Coalesce(Sum(
                        'credits__amount',
                        # Negate the Q object filter
                        filter=~Q(credits__nominal_account_number=reserved.VAT_CONTROL_ACCOUNT),
                    ), Decimal('0')),
                    vat=Coalesce(Sum(
                        'credits__amount',
                        filter=Q(credits__nominal_account_number=reserved.VAT_CONTROL_ACCOUNT),
                    ), Decimal('0')),
                )
                debit_notes = {d['contra_address_id']: d for d in debit_notes}

        with tracer.start_span('aggregate_results', child_of=request.span):
            objs = list()
            for p in purchases:
                # Get the debit note, if any
                dn = debit_notes.get(p['contra_address_id'])
                if dn is not None:
                    p['total_ex_vat'] -= dn['total_ex_vat']
                    p['vat'] -= dn['vat']

                p['total'] = p['total_ex_vat'] + p['vat']
                if p['total'] != Decimal('0'):
                    objs.append(p)

            order = cd['order']
            reverse = order.startswith('-')
            if reverse:
                order = order.lstrip('-')
            objs.sort(key=itemgetter(order), reverse=reverse)

        with tracer.start_span('gathering_metadata', child_of=request.span):
            page = controller.cleaned_data['page']
            limit = controller.cleaned_data['limit']
            total_records = len(objs)

            # Handle pagination
            objs = objs[page * limit: (page + 1) * limit]
            meta = {
                'total_records': total_records,
                'page': cd['page'],
                'limit': cd['limit'],
                'order': cd['order'],
                'warnings': controller.warnings,
            }

        with tracer.start_span('serializing_data', child_of=request.span) as span:
            span.set_tag('num_objects', len(objs))
            data = PurchasesAnalysisSerializer(instance=objs, many=True).data

        return Response({'content': data, '_metadata': meta})
