"""
Management for Payment Methods
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
from financial.controllers.payment_method import (
    PaymentMethodCreateController,
    PaymentMethodListController,
    PaymentMethodUpdateController,
)
from financial.models import PaymentMethod
from financial.permissions.payment_method import Permissions
from financial.serializers.payment_method import PaymentMethodSerializer


__all__ = [
    'PaymentMethodCollection',
    'PaymentMethodResource',
]


class PaymentMethodCollection(APIView):
    """
    Handles methods regarding Payment Method records that do not require an id to be specified, i.e. create, list
    """

    def get(self, request: Request) -> Response:
        """
        summary: Retrieve a list of Payment Method records

        description: |
            Retrieve a list of all Payment Method records for a Member

        responses:
            200:
                description: A list of Payment Method records, filtered and ordered by the User
            400: {}
        """
        tracer = settings.TRACER

        with tracer.start_span('validating_controller', child_of=request.span) as span:
            controller = PaymentMethodListController(data=request.GET, request=request, span=span)
            controller.is_valid()

        with tracer.start_span('retrieving_requested_objects', child_of=request.span):
            try:
                objs = PaymentMethod.objects.filter(
                    member_id=request.user.member['id'],
                    **controller.cleaned_data['search'],
                ).exclude(
                    **controller.cleaned_data['exclude'],
                ).order_by(
                    controller.cleaned_data['order'],
                )
            except (ValueError, ValidationError):
                return Http400(error_code='financial_payment_method_list_001')

        with tracer.start_span('gathering_metadata', child_of=request.span):
            total_records = objs.count()
            page = controller.cleaned_data['page']
            limit = controller.cleaned_data['limit']
            warnings = controller.warnings
            metadata = {
                'total_records': total_records,
                'page': page,
                'limit': limit,
                'warnings': warnings,
                'order': controller.cleaned_data['order'],
            }
            # Handle Pagination
            objs = objs[page * limit: (page + 1) * limit]

        with tracer.start_span('serializing_data', child_of=request.span):
            span.set_tag('num_objects', objs.count())
            data = PaymentMethodSerializer(instance=objs, many=True).data

        return Response({'content': data, '_metadata': metadata})

    def post(self, request: Request) -> Response:
        """
        summary: Create a new Payment Method record

        description: |
            Create a new Payment Method record with data supplied by the User

        responses:
            201:
                description: Payment record was created successfully
            400: {}
            403: {}
        """
        tracer = settings.TRACER

        with tracer.start_span('checking_permissions', child_of=request.span):
            err = Permissions.create(request)
            if err is not None:
                return err

        with tracer.start_span('validating_controller', child_of=request.span) as span:
            controller = PaymentMethodCreateController(data=request.data, request=request, span=span)
            if not controller.is_valid():
                return Http400(errors=controller.errors)

        with tracer.start_span('saving_object', child_of=request.span):
            # Create the object for the User's Member
            controller.cleaned_data['member_id'] = request.user.member['id']
            controller.instance.save()

        with tracer.start_span('serializing_data', child_of=request.span):
            data = PaymentMethodSerializer(instance=controller.instance).data

        return Response({'content': data}, status=status.HTTP_201_CREATED)


class PaymentMethodResource(APIView):
    """
    Handles methods regarding Payment Method records that require an id to be specified, i.e. read, update, delete
    """

    def get(self, request: Request, pk: int) -> Response:
        """
        summary: Read the details of a specific Payment Method record

        description: |
            Attempt to read a Payment Method record, returning a 404 if it does not exist

        path_params:
            pk:
                description: The id of the Payment Method record to be updated
                type: integer

        responses:
            200:
                description: Payment Method record was read successfully
            403: {}
            404: {}
        """
        tracer = settings.TRACER

        with tracer.start_span('retrieving_requested_object', child_of=request.span):
            try:
                obj = PaymentMethod.objects.get(
                    id=pk,
                    member_id=request.user.member['id'],
                )
            except PaymentMethod.DoesNotExist:
                return Http404(error_code='financial_payment_method_read_001')

        with tracer.start_span('serializing_data', child_of=request.span):
            data = PaymentMethodSerializer(instance=obj).data

        return Response({'content': data})

    def put(self, request: Request, pk: int, partial: bool = False) -> Response:
        """
        summary: Update the details of an existing Payment Method record

        description: |
            Attempt to update the details of an existing Payment Method. Returns a 404 if the record does not
            exist

        path_params:
            pk:
                description: The id of the Payment Method record to be updated
                type: integer

        responses:
            200:
                description: Payment Method record was updated successfully
            400: {}
            403: {}
            404: {}
        """
        tracer = settings.TRACER

        with tracer.start_span('checking_permissions', child_of=request.span):
            err = Permissions.update(request)
            if err is not None:
                return err

        with tracer.start_span('retrieving_requested_object', child_of=request.span):
            try:
                obj = PaymentMethod.objects.get(
                    id=pk,
                    member_id=request.user.member['id'],
                )
            except PaymentMethod.DoesNotExist:
                return Http404(error_code='financial_payment_method_update_001')

        with tracer.start_span('validating_controller', child_of=request.span) as span:
            controller = PaymentMethodUpdateController(
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
            data = PaymentMethodSerializer(instance=obj).data

        return Response({'content': data})

    def patch(self, request: Request, pk: int) -> Response:
        """
        Attempt to partially update a Payment Method record
        """
        return self.put(request, pk, True)

    def delete(self, request: Request, pk: int):
        """
        summary: Delete a specified Payment Method record

        description: |
            Attempt to delete a Payment Method record in the requesting User's Member by the given `pk`, returning a
            404 if it does not exist.

        path_params:
            pk:
                description: The id of the Payment Method record to delete
                type: integer

        responses:
            204:
                description: Payment Method record was deleted successfully
            403: {}
            404: {}
        """
        tracer = settings.TRACER

        with tracer.start_span('retrieving_requested_object', child_of=request.span):
            try:
                obj = PaymentMethod.objects.get(
                    id=pk,
                    member_id=request.user.member['id'],
                )
            except PaymentMethod.DoesNotExist:
                return Http404(error_code='financial_payment_method_delete_001')

        with tracer.start_span('checking_permissions', child_of=request.span):
            err = Permissions.delete(request)
            if err is not None:
                return err

        with tracer.start_span('saving_object', child_of=request.span):
            obj.set_deleted()

        return Response(status=status.HTTP_204_NO_CONTENT)
