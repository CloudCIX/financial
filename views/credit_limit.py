"""
Management for Credit Limit
"""
# stdlib
from decimal import Decimal
from typing import Dict
# libs
from cloudcix.api.membership import Membership
from cloudcix_rest.views import APIView
from django.conf import settings
from django.db.models import DecimalField, Sum
from django.db.models.functions import Coalesce
from rest_framework.request import Request
from rest_framework.response import Response
# local
from financial.models import NominalLedger


__all__ = [
    'CreditLimitCollection',
    'CreditLimitResource',
]

# Account Sale Invoice, Account Sale Credit Note, Account Sale Payment, Account Sale Adjustment
TRANSACTION_TYPES = [11002, 11003, 11004, 11005]


class CreditLimitCollection(APIView):
    """
    Handles methods regarding retrieving Credit Limit details that do not require an id to be specified, i.e. list
    """

    def get(self, request: Request) -> Response:
        """
        summary: Retrieve a list of Credit Limit details for all addresses linked to the requesting user's address.

        description: |
            List all addresses linked to the requesting user's address along with their max and current values of
            credit limit associated with the requesting address
            Note: get params for search will be passed straight to the address service

        responses:
            200:
                description: A list of Credit Limits, filtered and ordered by the User
        """
        tracer = settings.TRACER

        with tracer.start_span('construct_get_params', child_of=request.span):
            # By the time they reach the view, GET parameters have been updated by middleware, so they're in the form
            # {'search': {'address_id': 1, 'credit_limit': '5.00'}, 'exclude': {...}}. API calls expect params in the
            # form {'search[address_id]': 1, 'search[credit_limit]': '5.00', 'exclude[...]': '...'}
            params: Dict = dict()
            for outer_key, outer_value in request.GET.items():
                try:
                    # If the value is a dict, wrap its keys with the outer key
                    for inner_key, inner_value in outer_value.items():
                        if isinstance(inner_value, str) and inner_value.lower() in ['true', 'false']:
                            inner_value = inner_value.lower() == 'true'
                        params[f'{outer_key}[{inner_key}]'] = inner_value
                except AttributeError:
                    # The value is not a dict so add it to the params
                    params[outer_key] = outer_value

        with tracer.start_span('retrieve_linked_addresses', child_of=request.span) as span:
            response = Membership.address.list(
                token=request.user.token,
                params=params,
                span=span,
            )
            if response.status_code != 200:  # pragma: no cover
                return Response(response.json(), status=response.status_code)
            addresses = response.json()['content']
            metadata = response.json()['_metadata']

        with tracer.start_span('get_credit_limit_data', child_of=request.span) as span:
            # Now iterate through each address and get the credit values
            for address in addresses:
                # Can't list address links unfortunately
                response = Membership.address_link.read(
                    token=request.user.token,
                    pk=None,
                    address_id=address['id'],
                    span=span,
                )
                address['credit_limit'] = (response.json()['content']['credit_limit'])
                # Now also calculate the current credit value
                address['current_credit'] = NominalLedger.objects.filter(
                    address_id=request.user.address['id'],
                    contra_address_id=address['id'],
                    transaction_type_id__in=TRANSACTION_TYPES,
                ).aggregate(
                    balance=Coalesce(Sum('unallocated_balance'), 0, output_field=DecimalField()),
                )['balance']
        return Response({'content': addresses, '_metadata': metadata})


class CreditLimitResource(APIView):
    """
    Handles methods regarding retriving Credit Limit details that require an id to be specified, i.e. read
    """

    def get(self, request: Request, address_id: int) -> Response:
        """
        summary: Read the details of Credit Limit

        description: |
            Attempt to read Credit Limit details for a specific Address

        path_params:
            address_id:
                description: The id for the address whose credit limit is required
                type: integer

        responses:
            200:
                description: Credit Limit was read successfully
        """
        tracer = settings.TRACER

        with tracer.start_span('read_address', child_of=request.span):
            response = Membership.address.read(
                token=request.user.token,
                pk=address_id,
            )
            if response.status_code != 200:
                return Response(response.json(), status=response.status_code)
            address = response.json()['content']
            address['credit_limit'] = address.pop('link', {}).get('credit_limit')

        with tracer.start_span('get_current_credit', child_of=request.span):
            address['current_credit'] = Decimal(
                NominalLedger.objects.filter(
                    address_id=request.user.address['id'],
                    contra_address_id=address['id'],
                    transaction_type_id__in=TRANSACTION_TYPES,
                ).aggregate(
                    balance=Coalesce(Sum('unallocated_balance'), 0, output_field=DecimalField()),
                )['balance'],
            )
        return Response({'content': address})
