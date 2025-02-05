"""
Management for Period Ends
"""

# libs
from cloudcix_rest.exceptions import Http400, Http404
from cloudcix_rest.views import APIView
from django.conf import settings
from django.core.exceptions import ValidationError
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
# local
from financial.models.nominal_ledger import NominalLedger
from financial.controllers.period_end import (
    PeriodEndCreateController,
    PeriodEndListController,
)
from financial.permissions.period_end import Permissions
from financial.serializers.period_end import PeriodEndSerializer


__all__ = [
    'PeriodEndCollection',
    'PeriodEndResource',
]


class PeriodEndCollection(APIView):
    """
    Handles methods regarding Period Ends that don't require an id to be specified i.e. List, Create
    """

    def get(self, request: Request) -> Response:
        """
        summary: Retrieve a list of Period End transactions

        description: Retrieve a list of Nominal Ledger entries where the Transaction Type is for Period Ends

        responses:
            200:
                description: A list of Period End transactions, filtered and ordered by the User
            400: {}
        """
        tracer = settings.TRACER

        with tracer.start_span('validating_controller', child_of=request.span) as span:
            controller = PeriodEndListController(data=request.GET, request=request, span=span)
            # By validating the controller we generate the search filters
            controller.is_valid()

        with tracer.start_span('get_objects', child_of=request.span):
            order = controller.cleaned_data['order']
            try:
                objs = NominalLedger.period_end.filter(
                    address_id=request.user.address['id'],
                    **controller.cleaned_data['search'],
                ).exclude(
                    **controller.cleaned_data['exclude'],
                ).order_by(
                    order,
                )
            except (ValueError, ValidationError):
                return Http400(error_code='financial_period_end_list_001')

        with tracer.start_span('gathering_metadata', child_of=request.span):
            total_records = objs.count()
            page = controller.cleaned_data['page']
            limit = controller.cleaned_data['limit']
            # Handle pagination
            objs = objs[page * limit: (page + 1) * limit]
            metadata = {
                'page': page,
                'limit': limit,
                'order': order,
                'total_records': total_records,
                'warnings': controller.warnings,
            }

        with tracer.start_span('serializing_data', child_of=request.span) as span:
            span.set_tag('num_objects', objs.count())
            data = PeriodEndSerializer(instance=objs, many=True).data

        return Response({'content': data, '_metadata': metadata})

    def post(self, request: Request) -> Response:
        """
        summary: Create a new Period End record

        description: |
            Create a new entry on the Nominal Ledger where the transaction type is for Period Ends using data supplied
            by the User

        responses:
            201:
                description: Period End was created successfully
            400: {}
            403: {}
        """
        tracer = settings.TRACER

        with tracer.start_span('checking_permissions', child_of=request.span):
            err = Permissions.create(request)
            if err is not None:
                return err

        with tracer.start_span('validating_controller', child_of=request.span) as span:
            controller = PeriodEndCreateController(data=request.data, request=request, span=span)
            if not controller.is_valid():
                return Http400(errors=controller.errors)

        with tracer.start_span('saving_object', child_of=request.span):
            cd = controller.cleaned_data
            cd['address_id'] = cd['contra_address_id'] = request.user.address['id']
            cd['transaction_type_id'] = 12001
            controller.instance.save()

        with tracer.start_span('serializing_data', child_of=request.span):
            data = PeriodEndSerializer(instance=controller.instance).data

        return Response({'content': data}, status=status.HTTP_201_CREATED)


class PeriodEndResource(APIView):
    """
    Handles methods regarding Period Ends that do require an id to be specified i.e. Read, Delete
    """

    def get(self, request: Request, tsn: int) -> Response:
        """
        summary: Read the details of a specific Period End record

        description: |
            Attempt to read a Nominal Ledger entry by the given tsn where the Transaction Type is for Period Ends,
            returning a 404 if it does not exist

        path_params:
            tsn:
                description: The Transaction Sequence Number of the Period End to read
                type: integer

        responses:
            200:
                description: The Period End record was read successfully
            400: {}
            403: {}
        """
        tracer = settings.TRACER

        with tracer.start_span('retrieve_requested_object', child_of=request.span):
            try:
                obj = NominalLedger.period_end.get(
                    address_id=request.user.address['id'],
                    tsn=tsn,
                )
            except NominalLedger.DoesNotExist:
                return Http404(error_code='financial_period_end_read_001')

        with tracer.start_span('serializing_data', child_of=request.span):
            data = PeriodEndSerializer(instance=obj).data

        return Response({'content': data})

    def delete(self, request: Request, tsn: int) -> Response:
        """
        summary: Delete a Period End record

        description: |
            Attempt to delete a Nominal Ledger entry by the given tsn where the Transaction Type is for Period Ends,
            returning a 404 if it does not exist

        path_params:
            tsn:
                description: The Transaction Sequence Number of the Period End to delete
                type: integer

        responses:
            204:
                description: Period End record was deleted successfully
            403: {}
            404: {}
        """
        tracer = settings.TRACER

        with tracer.start_span('retrieve_requested_object', child_of=request.span):
            try:
                obj = NominalLedger.period_end.get(
                    address_id=request.user.address['id'],
                    tsn=tsn,
                )
            except NominalLedger.DoesNotExist:
                return Http404(error_code='financial_period_end_delete_001')

        with tracer.start_span('checking_permissions', child_of=request.span):
            err = Permissions.delete(request, obj)
            if err is not None:
                return err

        with tracer.start_span('saving_object', child_of=request.span):
            obj.set_deleted()

        return Response(status=status.HTTP_204_NO_CONTENT)
