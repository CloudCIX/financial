"""
Management for the Sales by Territory service
This view presents aggregated data from the Nominal Ledger
"""

# stdlib
from decimal import Decimal
# libs
from cloudcix.api.membership import Membership
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
from financial.controllers.sales_by_territory import SalesByTerritoryListController
from financial.models import NominalLedger
from financial.serializers.sales_by_territory import SalesByTerritorySerializer


__all__ = [
    'SalesByTerritoryCollection',
]


class SalesByTerritoryCollection(APIView):
    """
    Handles methods regarding the Nominal Ledger that don't require an id to be specified i.e. list
    """

    def get(self, request: Request, territory_id: int) -> Response:
        """
        summary: Get the total amounts sold to each Address in a Territory

        description: |
            Calculate the total amount sold to Addresses that are linked to the requesting User's Address by the
            specified Territory. The totals are calculated as the Sale Invoices less the Credit Notes

        path_params:
            territory_id:
                description: The id of a Territory linking the requesting User's Address to customer Addresses
                type: integer

        responses:
            200:
                description: A list of Addresses with the total amount sold to each one
            400: {}
        """
        tracer = settings.TRACER

        with tracer.start_span('validating_controller', child_of=request.span) as span:
            controller = SalesByTerritoryListController(data=request.GET, request=request, span=span)
            # By validating the controller we generate the filters
            controller.is_valid()

        with tracer.start_span('get_addresses', child_of=request.span) as span:
            cd = controller.cleaned_data
            params = {
                'search[address_link__territory__id]': territory_id,
                'page': cd['page'],
                'limit': cd['limit'],
                'order': cd['order'],
            }
            membership_response = Membership.address.list(
                token=request.user.token,
                params=params,
                span=span,
            )

            addresses = membership_response.json()['content']
            address_ids = [a['id'] for a in addresses]

        with tracer.start_span('get_objects', child_of=request.span) as span:
            if len(address_ids) != 0:
                with tracer.start_span('get_debits', child_of=span):
                    try:
                        # Calculate all sales from invoices. Search for the credit lines on the invoices as they will
                        # show how much of the invoice was VAT
                        debits = NominalLedger.objects.filter(
                            address_id=request.user.address['id'],
                            contra_address_id__in=address_ids,
                            transaction_type_id__in=(11000, 11002),
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
                    except (ValueError, ValidationError):
                        return Http400(error_code='financial_sales_by_territory_list_001')

                with tracer.start_span('get_credits', child_of=span):
                    # Calculate the amounts lost from credit notes. Search for the debit lines on the credit notes as
                    # they will show how much of the transaction was vat
                    credits = NominalLedger.objects.filter(
                        address_id=request.user.address['id'],
                        contra_address_id__in=address_ids,
                        transaction_type_id__in=(11001, 11003),
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

        with tracer.start_span('aggregate_results', child_of=request.span):
            # Get the debit - credit total for each Contra Address
            for address in addresses:
                total_ex_vat = vat = Decimal('0.0000')

                for d in debits:
                    if address['id'] == d['contra_address_id']:
                        total_ex_vat += d['total_ex_vat']
                        vat += d['vat']
                        break

                for c in credits:
                    if address['id'] == c['contra_address_id']:
                        total_ex_vat -= c['total_ex_vat']
                        vat -= c['vat']
                        break
                address['total_ex_vat'] = total_ex_vat.quantize(Decimal('0.0000'))
                address['vat'] = vat.quantize(Decimal('0.0000'))
                address['total'] = address['total_ex_vat'] + address['vat']

        with tracer.start_span('gathering_metadata', child_of=request.span):
            # There's one record for each Address in the Territory
            total_records = membership_response.json()['_metadata']['total_records']
            meta = {
                'total_records': total_records,
                'page': cd['page'],
                'limit': cd['limit'],
                'order': cd['order'],
                'warnings': controller.warnings,
            }

        with tracer.start_span('serializing_data', child_of=request.span) as span:
            span.set_tag('num_objects', len(addresses))
            data = SalesByTerritorySerializer(instance=addresses, many=True).data

        return Response({'content': data, '_metadata': meta})
