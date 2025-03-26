"""
Management for Allocations
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
from financial.controllers.allocation import (
    AllocationCreateController,
    AllocationListController,
)
from financial.models import Allocation, AllocationDetail
from financial.permissions.allocation import Permissions
from financial.serializers import AllocationSerializer


__all__ = [
    'AllocationCollection',
    'AllocationResource',
]


class AllocationCollection(APIView):
    """
    Handles methods regarding Account Purchase Adjustments that don't require an id to be specified, i.e. create, list
    """

    def get(self, request: Request) -> Response:
        """
        summary: Retrieve a list of Allocation records

        description: |
            Retrieve a list of all Allocation records for an Address. An 'allocation_type' must be sent in the search
            request. 'supplier' and 'customer' are the two valid values.

            A Supplier allocation_type' will return a list of allocations from the Purchases Ledger.

            A Customer allocation_type' will return a list of allocations from the Sales Ledger.

        responses:
            200:
                description: A list of Allocation records, filtered and ordered by the User
            400: {}
        """
        tracer = settings.TRACER

        with tracer.start_span('validating_controller', child_of=request.span) as span:
            controller = AllocationListController(data=request.GET, request=request, span=span)
            controller.is_valid()

        with tracer.start_span('get_allocation_type', child_of=request.span):
            allocation_type = controller.cleaned_data['search'].pop('allocation_type', '').lower()
            if allocation_type == 'customer':
                number = 1300
            elif allocation_type == 'supplier':
                number = 2200
            else:
                return Http400(error_code='financial_allocation_list_001')

        with tracer.start_span('retrieve_requested_objects', child_of=request.span):
            try:
                objs = Allocation.objects.filter(
                    address_id=request.user.address['id'],
                    nominal_account_number=number,
                    **controller.cleaned_data['search'],
                ).exclude(
                    **controller.cleaned_data['exclude'],
                ).order_by(
                    controller.cleaned_data['order'],
                ).distinct()
            except (ValueError, ValidationError):
                return Http400(error_code='financial_allocation_list_002')

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
            data = AllocationSerializer(instance=objs, many=True).data

        return Response({'content': data, '_metadata': metadata})

    def post(self, request: Request) -> Response:
        """
        summary: |
            Create an Allocation record for a set of Transactions allocating certain amounts of debits and credits
            against each other

        description: |
            The total amount of debits and credits must balance to 0.The allocated transactions must belong to the
            same contra_address and the allocated amount cannot be greater than the unallocated_balance of the
            transaction.

            Finally, the allocated Transactions must be compatible i.e

            Account Sale Invoices can be allocated against:
            - Account Sale Credit Notes
            - Account Sale Adjustments
            - Account Sale Payments

            Account Purchase Invoices can be allocated against:
            - Account Purchase Debit Notes
            - Account Purchase Adjustments
            - Account Purchase Payments

        responses:
            200:
                description: Nominal Ledger record was created successfully
            400: {}
            403: {}
        """

        tracer = settings.TRACER

        with tracer.start_span('checking_permissions', child_of=request.span):
            err = Permissions.create(request)
            if err is not None:
                return err

        with tracer.start_span('validating_controller', child_of=request.span) as span:
            controller = AllocationCreateController(data=request.data, request=request, span=span)
            if not controller.is_valid():
                return Http400(errors=controller.errors)

        with tracer.start_span('setting_address_id', child_of=request.span):
            # Remove the details before calling controller.instance
            details = controller.cleaned_data.pop('details')
            obj = controller.instance
            obj.address_id = request.user.address['id']

        with tracer.start_span('saving_objects', child_of=request.span) as span:
            with tracer.start_span('saving_allocation', child_of=span):
                obj.save()
            with tracer.start_span('saving_allocation_details', child_of=span):
                for line in details:
                    credit_amount = line['amount'] if line['amount'] < 0 else 0
                    debit_amount = line['amount'] if line['amount'] > 0 else 0
                    AllocationDetail.objects.create(
                        allocation=obj,
                        credit_amount=credit_amount,
                        debit_amount=debit_amount,
                        nominal_ledger=line['nominal_ledger'],
                    )
        with tracer.start_span('serializing_data', child_of=span):
            data = AllocationSerializer(instance=obj).data

        return Response({'content': data}, status=status.HTTP_201_CREATED)


class AllocationResource(APIView):

    def delete(self, request: Request, pk: int) -> Response:
        """
        summary: Delete a specified Allocation record

        description: |
            Attempt to delete an Allocation record, returning a 404 if it does not exist
            When an Allocation is deleted the Transactions involved in the Allocation will automatically have their
            Unallocated Balance restored by the allocated amount.

        path_params:
            pk:
                description: The id of the Allocation record to delete
                type: integer

        responses:
            204:
                description: Allocation record was deleted successfully
            403: {}
            404: {}
        """
        tracer = settings.TRACER

        with tracer.start_span('retrieving_requested_object', child_of=request.span):
            try:
                obj = Allocation.objects.get(id=pk)
            except Allocation.DoesNotExist:
                return Http404(error_code='financial_allocation_delete_001')

        with tracer.start_span('checking_permissions', child_of=request.span):
            err = Permissions.delete(request, obj)
            if err is not None:
                return err

        with tracer.start_span('saving_object', child_of=request.span):
            obj.set_deleted()

        return Response(status=status.HTTP_204_NO_CONTENT)
