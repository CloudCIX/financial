"""
Management for Tax Rates
"""
# libs
from cloudcix_rest.exceptions import Http400, Http404
from django.core.exceptions import ValidationError
from django.conf import settings
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
# local
from financial.api_view import FinancialAPIView as APIView
from financial.controllers.tax_rate import (
    TaxRateCreateController,
    TaxRateListController,
    TaxRateUpdateController,
)
from financial.models.tax_rate import TaxRate
from financial.permissions.tax_rate import Permissions
from financial.serializers.tax_rate import TaxRateSerializer


__all__ = [
    'TaxRateCollection',
    'TaxRateResource',
]


class TaxRateCollection(APIView):
    """
    Handles methods regarding Tax Rate records that do not require an id to be specified, i.e. create, list
    """

    def get(self, request: Request) -> Response:
        """
        summary: Retrieve a list of Tax Rate records

        description: |
            Retrieve a list of all Tax Rate records for the User's Address

        responses:
            200:
                description: A list of Tax Rates, filtered and ordered by the User
            400: {}
        """
        tracer = settings.TRACER
        with tracer.start_span('validating_controller', child_of=request.span) as span:
            controller = TaxRateListController(data=request.GET, span=span)
            # By validating the controller we generate the filters
            controller.is_valid()

        with tracer.start_span('retrieve_requested_objects', child_of=request.span):
            try:
                objs = TaxRate.objects.filter(
                    address_id=request.user.address['id'],
                    **controller.cleaned_data['search'],
                ).exclude(
                    **controller.cleaned_data['exclude'],
                ).order_by(
                    controller.cleaned_data['order'],
                )
            except (ValueError, ValidationError):
                return Http400(error_code='financial_tax_rate_list_001')

        with tracer.start_span('gathering_metadata', child_of=request.span):
            total_records = objs.count()
            page = controller.cleaned_data['page']
            limit = controller.cleaned_data['limit']
            warnings = controller.warnings
            metadata = {
                'page': page,
                'limit': limit,
                'order': controller.cleaned_data['order'],
                'warnings': warnings,
                'total_records': total_records,
            }
            # Handle pagination
            objs = objs[page * limit:(page + 1) * limit]

        with tracer.start_span('serializing_data', child_of=request.span):
            span.set_tag('num_objects', objs.count())
            data = TaxRateSerializer(instance=objs, many=True).data

        return Response({'content': data, '_metadata': metadata})

    def post(self, request: Request) -> Response:
        """
        summary: Create a new Tax Rate record

        description: |
            Create a new Tax Rate record using data supplied by the User

        responses:
            201:
                description: Tax Rate record was created successfully
            400: {}
            403: {}
        """
        tracer = settings.TRACER

        with tracer.start_span('checking_permissions', child_of=request.span):
            err = Permissions.create(request)
            if err is not None:
                return err

        with tracer.start_span('validating_controller', child_of=request.span) as span:
            controller = TaxRateCreateController(data=request.data, request=request, span=span)
            if not controller.is_valid():
                return Http400(errors=controller.errors)

        with tracer.start_span('saving_object', child_of=request.span):
            controller.cleaned_data['address_id'] = request.user.address['id']
            controller.instance.save()

        with tracer.start_span('serializing_data', child_of=request.span):
            data = TaxRateSerializer(instance=controller.instance).data

        return Response({'content': data}, status=status.HTTP_201_CREATED)


class TaxRateResource(APIView):
    """
    Handles methods regarding Tax Rate records that require an id to be specified, i.e. read, update, delete
    """

    def get(self, request: Request, pk: int) -> Response:
        """
        summary: Read the details of a specific Tax Rate record

        description: |
            Attempt to read a Tax Rate record, returning a 404 if it does not exist

        path_params:
            pk:
                description: The id of the Tax Rate record to be retrieved
                type: integer

        responses:
            200:
                description: Tax Rate was read successfully
            403: {}
            404: {}
        """
        tracer = settings.TRACER

        with tracer.start_span('retrieving_requested_object', child_of=request.span):
            try:
                obj = TaxRate.objects.get(id=pk)
            except TaxRate.DoesNotExist:
                return Http404(error_code='financial_tax_rate_read_001')

        with tracer.start_span('checking_permissions', child_of=request.span) as span:
            err = Permissions.read(request, obj, span)
            if err is not None:
                return err

        with tracer.start_span('serializing_data', child_of=request.span):
            data = TaxRateSerializer(instance=obj).data

        return Response({'content': data})

    def put(self, request: Request, pk: int, partial: bool = False) -> Response:
        """
        summary: Update the details of an existing Tax Rate record

        description: |
            Attempt to update the details of an existing Tax Rate, returning a 404 if it does not exist

        path_params:
            pk:
                description: The id of the Tax Rate record to be updated
                type: integer

        responses:
            200:
                description: Tax Rate record was updated successfully
            400: {}
            403: {}
            404: {}
        """
        tracer = settings.TRACER

        with tracer.start_span('retrieving_requested_object', child_of=request.span):
            try:
                obj = TaxRate.objects.get(id=pk)
            except TaxRate.DoesNotExist:
                return Http404(error_code='financial_tax_rate_update_001')

        with tracer.start_span('checking_permissions', child_of=request.span):
            err = Permissions.update(request, obj)
            if err is not None:
                return err

        with tracer.start_span('validating_controller', child_of=request.span) as span:
            controller = TaxRateUpdateController(
                instance=obj,
                data=request.data,
                partial=partial,
                request=request,
                span=span,
            )
            if not controller.is_valid():
                return Http400(errors=controller.errors)

        with tracer.start_span('saving_object', child_of=request.span):
            controller.instance.save()

        with tracer.start_span('serializing_data', child_of=request.span):
            data = TaxRateSerializer(instance=controller.instance).data

        return Response({'content': data})

    def patch(self, request: Request, pk: int) -> Response:
        """
        Attempt to partially update a Tax Rate record
        """
        return self.put(request, pk, True)

    def delete(self, request: Request, pk: int) -> Response:
        """
        summary: Delete a specified Tax Rate record

        description: |
            Attempt to delete a Tax Rate record, returning a 404 if it does not exist

        path_params:
            pk:
                description: The id of the Tax Rate record to delete
                type: integer

        responses:
            204:
                description: Tax Rate record was deleted successfully
            403: {}
            404: {}
        """
        tracer = settings.TRACER

        with tracer.start_span('retrieving_requested_object', child_of=request.span):
            try:
                obj = TaxRate.objects.get(id=pk)
            except TaxRate.DoesNotExist:
                return Http404(error_code='financial_tax_rate_delete_001')

        with tracer.start_span('checking_permissions', child_of=request.span):
            err = Permissions.delete(request, obj)
            if err is not None:
                return err

        with tracer.start_span('saving_object', child_of=request.span):
            obj.set_deleted()

        return Response(status=status.HTTP_204_NO_CONTENT)
