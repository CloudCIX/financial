"""
Management for Nominal Accounts
"""

# stdlib
from typing import cast
# libs
from cloudcix_rest.exceptions import Http400, Http404
from django.db.models import Prefetch
from django.conf import settings
from django.core.exceptions import ValidationError
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
# local
from financial.api_view import FinancialAPIView as APIView
from financial.controllers import (
    GlobalNominalAccountCreateController,
    GlobalNominalAccountListController,
    GlobalNominalAccountUpdateController,
)
from financial.models import AddressNominalAccount, GlobalNominalAccount
from financial.permissions.global_nominal_account import Permissions
from financial.serializers import GlobalNominalAccountSerializer


__all__ = [
    'GlobalNominalAccountCollection',
    'GlobalNominalAccountResource',
]


class GlobalNominalAccountCollection(APIView):
    """
    Handles methods regarding Global Nominal Account records that do not require an id to be specified, i.e. create,
    list
    """

    def get(self, request: Request) -> Response:
        """
        summary: Retrieve a list of Nominal Account records

        description: |
            Retrieve a list of all Nominal Account records for a Member. If a Nominal Account has been customised
            for an Address in the Member, the Address-specific details will be returned in the response.

        responses:
            200:
                description: A list of Nominal Accounts, filtered and ordered by the User
            400: {}
        """
        tracer = settings.TRACER

        with tracer.start_span('validating_controller', child_of=request.span) as span:
            controller = GlobalNominalAccountListController(data=request.GET, span=span)
            # By validating the controller we generate the filters
            controller.is_valid()

        with tracer.start_span('get_objects', child_of=request.span) as span:
            try:
                objs = GlobalNominalAccount.objects.filter(
                    member_id=request.user.member['id'],
                    **controller.cleaned_data['search'],
                ).prefetch_related(
                    Prefetch(
                        lookup='address_nominal_accounts',
                        queryset=AddressNominalAccount.objects.filter(address_id=request.user.address['id']),
                    ),
                ).exclude(
                    **controller.cleaned_data['exclude'],
                ).order_by(
                    controller.cleaned_data['order'],
                )
            except (ValueError, ValidationError):
                return Http400(error_code='financial_global_nominal_account_list_001')

        # Gather the metadata
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

        # Now that we only have the objects that the User requested, go through each item and over-write the Member
        # specific account data with that of the Address Account
        with tracer.start_span('update_returned_data', child_of=request.span):
            for account in objs:
                try:
                    address_account = account.address_nominal_accounts.all()[0]
                    account.address_id = address_account.address_id
                    account.description = address_account.description
                    account.currency_id = address_account.currency_id
                except IndexError:
                    # The Global Nominal Account has no Address Account for the given Address
                    pass

        with tracer.start_span('serializing_data', child_of=request.span) as span:
            span.set_tag('num_objects', len(objs))
            data = GlobalNominalAccountSerializer(instance=objs, many=True).data

        return Response({'content': data, '_metadata': metadata})

    def post(self, request: Request) -> Response:
        """
        summary: Create a new Global Nominal Account record

        description: |
            Create a new Global Nominal Account record using data supplied by the User

        responses:
            201:
                description: Global Nominal Account record was created successfully
            400: {}
            403: {}
        """
        tracer = settings.TRACER

        with tracer.start_span('validating_controller', child_of=request.span) as span:
            controller = GlobalNominalAccountCreateController(data=request.data, request=request, span=span)
            if not controller.is_valid():
                return Http400(errors=controller.errors)

        with tracer.start_span('checking_permissions', child_of=request.span):
            err = Permissions.create(request)
            if err is not None:
                return err

        with tracer.start_span('saving_object', child_of=request.span) as span:
            # Create the Global Nominal Account for the User's Member
            controller.cleaned_data['member_id'] = request.user.member['id']
            controller.instance.save()

        with tracer.start_span('serializing_data', child_of=request.span):
            data = GlobalNominalAccountSerializer(instance=controller.instance).data

        return Response({'content': data}, status=status.HTTP_201_CREATED)


class GlobalNominalAccountResource(APIView):
    """
    Handles methods regarding Global Nominal Account records that require an id to be specified, i.e. read, update,
    delete
    """

    def get(self, request: Request, pk: int) -> Response:
        """
        summary: Read the details of a specific Nominal Account record

        description: |
            Attempt to read a Nominal Account record, returning a 404 if it does not exist. If the Account has been
            customised for an Address, the Address-specific details will be returned in the response if the Address
            id is supplied

        path_params:
            pk:
                description: The id of the Global Nominal Account record to be retrieved
                type: integer

        responses:
            200:
                description: Nominal Account was read successfully
            404: {}
        """
        tracer = settings.TRACER

        with tracer.start_span('checking_address_id', child_of=request.span):
            address_id = request.GET.get('address_id', False)
            if request.user.global_active and address_id:
                try:
                    address_id = int(cast(int, address_id))
                except (TypeError, ValueError):
                    return Http400(error_code='financial_global_nominal_account_read_001')
            elif not request.user.global_active:
                address_id = request.user.address['id']

            if address_id:
                prefetch = Prefetch(
                    'address_nominal_accounts',
                    AddressNominalAccount.objects.filter(address_id=address_id),
                )
            else:
                prefetch = None

        with tracer.start_span('retrieving_requested_object', child_of=request.span):
            try:
                obj = GlobalNominalAccount.objects.prefetch_related(
                    prefetch,
                ).get(
                    id=pk,
                    member_id=request.user.member['id'],
                )
            except GlobalNominalAccount.DoesNotExist:
                return Http404(error_code='financial_global_nominal_account_read_002')

            try:
                address_account = obj.address_nominal_accounts.all()[0]
                obj.address_id = address_account.address_id
                obj.currency_id = address_account.currency_id
                obj.description = address_account.description
            except IndexError:
                pass

        with tracer.start_span('serializing_data', child_of=request.span):
            data = GlobalNominalAccountSerializer(instance=obj).data

        return Response({'content': data})

    def put(self, request: Request, pk: int, partial: bool = False) -> Response:
        """
        summary: Update the details of an existing Nominal Account record

        description: |
            Attempt to update the details of an existing Global Nominal Account. Returns a 404 if the record does not
            exist. If an Address id is passed in, the Address Nominal Account that is linked to the Global Nominal
            Account will be updated. If the Address Nominal Account does not exist it will be created.

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

        with tracer.start_span('retrieving_requested_object', child_of=request.span):
            try:
                obj = GlobalNominalAccount.objects.get(id=pk)
            except GlobalNominalAccount.DoesNotExist:
                return Http404(error_code='financial_global_nominal_account_update_001')

        with tracer.start_span('validating_controller', child_of=request.span) as span:
            controller = GlobalNominalAccountUpdateController(
                instance=obj,
                data=request.data,
                request=request,
                partial=partial,
                span=span,
            )
            if not controller.is_valid():
                return Http400(errors=controller.errors)
            address_id = controller.cleaned_data.pop('address_id', None)

        with tracer.start_span('checking_permissions', child_of=request.span):
            err = Permissions.update(request, address_id)
            if err is not None:
                return err

        if not address_id:
            with tracer.start_span('saving_global_account', child_of=span):
                # The User is updating a Global Nominal Account
                controller.instance.save()
        else:
            with tracer.start_span('saving_address_account', child_of=span):
                try:
                    address_obj = AddressNominalAccount.objects.get(
                        address_id=address_id,
                        global_nominal_account=obj,
                    )
                except AddressNominalAccount.DoesNotExist:
                    # Create the Address Account with the default values coming from the Global Nominal Account
                    address_obj = AddressNominalAccount(
                        address_id=address_id,
                        global_nominal_account=obj,
                        currency_id=obj.currency_id,
                        description=obj.description,
                    )
                # Now that we have an Address Nominal Account, update it with the controller data
                cd = controller.cleaned_data
                if cd.get('currency_id', False):
                    address_obj.currency_id = cd['currency_id']
                if cd.get('description', False):
                    address_obj.description = cd['description']
                address_obj.save()

        with tracer.start_span('serializing_data', child_of=request.span):
            data = GlobalNominalAccountSerializer(instance=controller.instance).data

        return Response({'content': data})

    def patch(self, request: Request, pk: int) -> Response:
        """
        Attempt to partially update a Nominal Account record
        """
        return self.put(request, pk, True)

    def delete(self, request: Request, pk: int) -> Response:
        """
        summary: Delete a specified Global Nominal Account record

        description: |
            Attempt to delete a Global Nominal Account record in the requesting User's Member by the given `pk`,
            returning a 404 if it does not exist.

        path_params:
            pk:
                description: The id of the Global Nominal Account record to delete
                type: integer

        responses:
            204:
                description: Global Nominal Account record was deleted successfully
            403: {}
            404: {}
        """
        tracer = settings.TRACER

        with tracer.start_span('retrieving_requested_object', child_of=request.span):
            try:
                obj = GlobalNominalAccount.objects.prefetch_related('address_nominal_accounts').get(id=pk)
            except GlobalNominalAccount.DoesNotExist:
                return Http404(error_code='financial_global_nominal_account_delete_001')

        with tracer.start_span('checking_permissions', child_of=request.span):
            err = Permissions.delete(request, obj)
            if err is not None:
                return err

        with tracer.start_span('saving_object', child_of=request.span):
            obj.set_deleted()

        return Response(status=status.HTTP_204_NO_CONTENT)
