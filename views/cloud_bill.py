
"""
Access to the Financial DB for Cloudbill purposes
"""
# stdlib
from typing import Dict
# libs
from django.conf import settings
from django.db.models import Func, Sum
from rest_framework.request import Request
from rest_framework.response import Response
# local
from financial import reserved_accounts as reserved
from financial.api_view import FinancialAPIView as APIView
from financial.models import NominalLedgerCredit

__all__ = [
    'CloudbillResource',
]


class StripProductName(Func):
    function = 'REGEXP_MATCHES'
    template = "(%(function)s(%(expressions)s, '^([A-Za-z]+ #[0-9]+).*$'))[1]"


class CloudbillResource(APIView):
    """
    Generate the data for a Cloudbill Project
    """

    def get(self, request: Request, project_id: int) -> Response:
        """
        summary: Get the amount of unit hours already billed for everything in the given Project

        description: |
            Get the total number of unit hours that have already been billed for the Project that is provided.
            Use the Description and Part Number fields for grouping and get the sum of the Quantity Fields for all
            invoices that fit the narrative pattern

        path_params:
            project_id:
                description: The ID of the Project to get the historical data for
                type: integer

        responses:
            200:
                description: The total number of billed unit hours for the Project currently
                content:
                    application/json:
                        schema:
                            type: object
                            additionalProperties:
                                type: object
                                additionalProperties:
                                    type: string
            400: {}
            403: {}
        """
        tracer = settings.TRACER

        with tracer.start_span('retrieving_data', child_of=request.span):
            narrative = f'Invoice for Project #{project_id}'
            kw = {
                'nominal_ledger__transaction_type_id': 11002,
                'nominal_ledger__narrative': narrative,
            }
            if request.user.id != 1:
                kw['nominal_ledger__address_id'] = request.user.address['id']
            data = NominalLedgerCredit.objects.exclude(
                nominal_account_number=reserved.VAT_CONTROL_ACCOUNT,
            ).filter(**kw).annotate(
                identifier=StripProductName('description'),
            ).values(
                'identifier',
                'part_number',
            ).annotate(hours_billed=Sum('quantity'))

        with tracer.start_span('generate_sku_map', child_of=request.span):
            # Given the data from the db in a list of dicts of {desc, part_num, hours_billed}
            # Convert it into a dict of {desc: {part_num: hours}}
            response: Dict[str, Dict[str, float]] = {}

            for group in data:
                identifier = group['identifier']
                part_number = group['part_number']
                hours_billed = group['hours_billed']

                if identifier in response:
                    response[identifier][part_number] = hours_billed
                else:
                    response[identifier] = {part_number: hours_billed}

        return Response({'content': response})
