"""
Management for Nominal Contra
"""
# libs
from cloudcix_rest.exceptions import Http400, Http404
from django.conf import settings
from django.core.exceptions import ValidationError
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
# local
from financial.api_view import FinancialAPIView as APIView
from financial.controllers.nominal_contra import (
    NominalContraCreateController,
    NominalContraListController,
    NominalContraUpdateController,
)
from financial.models.nominal_contra import NominalContra
from financial.permissions.nominal_contra import Permissions
from financial.serializers.nominal_contra import NominalContraSerializer


__all__ = [
    'NominalContraCollection',
    'NominalContraResource',
]


class NominalContraCollection(APIView):
    """
    Handles methods regarding Nominal Contra records that do not require an id to be specified, i.e. create, list
    """

    def get(self, request: Request) -> Response:
        """
        summary: Retrieve a list of Nominal Contra records

        description: |
            Retrieve a list of all Nominal Contra records for a Member

        responses:
            200:
                description: A list of Nominal Contra records, filtered and ordered by the User
            400: {}
        """
        tracer = settings.TRACER

        with tracer.start_span('validating_controller', child_of=request.span) as span:
            controller = NominalContraListController(data=request.GET, span=span)
            # By validating the controller we generate the filters
            controller.is_valid()

        with tracer.start_span('retrieve_requested_objects', child_of=request.span):
            try:
                objs = NominalContra.objects.filter(
                    payment_method__member_id=request.user.member['id'],
                    **controller.cleaned_data['search'],
                ).exclude(
                    **controller.cleaned_data['exclude'],
                ).order_by(
                    controller.cleaned_data['order'],
                )
            except (ValueError, ValidationError):
                return Http400(error_code='financial_nominal_contra_list_001')

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
            data = NominalContraSerializer(instance=objs, many=True).data

        return Response({'content': data, '_metadata': metadata})

    def post(self, request: Request) -> Response:
        """
        summary: Create a new Nominal Contra record

        description: |
            Create a new Nominal Contra record using the data supplied by the User

        responses:
            201:
                description: Nominal Contra record was created successfully
            400: {}
            403: {}
        """
        tracer = settings.TRACER

        with tracer.start_span('checking_permissions', child_of=request.span):
            err = Permissions.create(request)
            if err is not None:
                return err

        with tracer.start_span('validating_controller', child_of=request.span) as span:
            controller = NominalContraCreateController(data=request.data, request=request, span=span)
            if not controller.is_valid():
                return Http400(errors=controller.errors)

        with tracer.start_span('saving_object', child_of=request.span):
            controller.instance.save()

        with tracer.start_span('serializing_data', child_of=request.span):
            data = NominalContraSerializer(instance=controller.instance).data

        return Response({'content': data}, status=status.HTTP_201_CREATED)


class NominalContraResource(APIView):
    """
    Handles methods regarding Nominal Contra records that require an id to be specified, i.e. read, update, delete
    """

    def get(self, request: Request, pk: int) -> Response:
        """
        summary: Read the details of a specific Nominal Contra record

        description: |
            Attempt to read a Nominal Contra record, returning a 404 if it does not exist

        path_params:
            pk:
                description: The id of the Nominal Contra record to be retrieved
                type: integer

        responses:
            200:
                description: Nominal Account was read successfully
            404: {}
        """
        tracer = settings.TRACER

        with tracer.start_span('retrieve_requested_object', child_of=request.span):
            try:
                obj = NominalContra.objects.get(
                    id=pk,
                    payment_method__member_id=request.user.member['id'],
                )
            except NominalContra.DoesNotExist:
                return Http404(error_code='financial_nominal_contra_read_001')

        with tracer.start_span('serializing_data', child_of=request.span):
            data = NominalContraSerializer(instance=obj).data

        return Response({'content': data})

    def put(self, request: Request, pk: int, partial: bool = False) -> Response:
        """
        summary: Update the details of an existing Nominal Account record

        description: |
            Attempt to update the details of an existing Nominal Contra. Returns a 404 if the record does not
            exist.

        path_params:
            pk:
                description: The id of the Global Nominal Account record to be updated
                type: integer

        responses:
            200:
                description: Nominal Account record was updated successfully
            400: {}
            403: {}
            404: {}
        """
        tracer = settings.TRACER

        with tracer.start_span('checking_permissions', child_of=request.span):
            err = Permissions.update(request)
            if err is not None:
                return err

        with tracer.start_span('retrieve_requested_object', child_of=request.span):
            try:
                obj = NominalContra.objects.get(
                    id=pk,
                    payment_method__member_id=request.user.member['id'],
                )
            except NominalContra.DoesNotExist:
                return Http404(error_code='financial_nominal_contra_update_001')

        with tracer.start_span('validating_controller', child_of=request.span) as span:
            controller = NominalContraUpdateController(
                instance=obj,
                data=request.data,
                request=request,
                partial=partial,
                span=span,
            )
            if not controller.is_valid():
                return Http400(errors=controller.errors)

        with tracer.start_span('saving_object', child_of=request.span):
            controller.instance.save()

        with tracer.start_span('serializing_data', child_of=request.span):
            data = NominalContraSerializer(instance=controller.instance).data

        return Response({'content': data})

    def patch(self, request: Request, pk: int) -> Response:
        """
        Attempt to partially update a Nominal Contra record
        """
        return self.put(request, pk, True)

    def delete(self, request: Request, pk: int) -> Response:
        """
        summary: Delete a specified Global Nominal Account record

        description: |
            Attempt to delete a Nominal Contra record in the requesting User's Member by the given `pk`, returning a 404
            if it does not exist.

        path_params:
            pk:
                description: The id of the Nominal Contra record to delete
                type: integer

        responses:
            204:
                description: Nominal Contra record was deleted successfully
            403: {}
            404: {}
        """
        tracer = settings.TRACER

        with tracer.start_span('checking_permissions', child_of=request.span):
            err = Permissions.delete(request)
            if err is not None:
                return err

        with tracer.start_span('retrieving_requested_object', child_of=request.span):
            try:
                obj = NominalContra.objects.get(
                    id=pk,
                    payment_method__member_id=request.user.member['id'],
                )
            except NominalContra.DoesNotExist:
                return Http404(error_code='financial_nominal_contra_delete_001')

        with tracer.start_span('saving_object', child_of=request.span):
            obj.set_deleted()

        return Response(status=status.HTTP_204_NO_CONTENT)
