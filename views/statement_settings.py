"""
Management for Statement Setting records
"""
# stdlib
import calendar
from datetime import datetime
from typing import Optional
# libs
from cloudcix_rest.exceptions import Http400
from cloudcix_rest.views import APIView
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db.models import Q
from rest_framework.request import Request
from rest_framework.response import Response
# local
from financial.controllers.statement_settings import (
    StatementSettingsListController,
    StatementSettingsUpdateController,
)
from financial.models import StatementSettings
from financial.permissions.statement_settings import Permissions
from financial.serializers.statement_settings import StatementSettingsSerializer


__all__ = [
    'StatementSettingsCollection',
    'StatementSettingsResource',
]


class StatementSettingsCollection(APIView):
    """
    Handles methods regarding Statement Settings records that don't require an id to be specified
    """

    def get(self, request: Request) -> Response:
        """
        summary: |
            Retrieve a list of Statement Setting records

        description: |
           Retrieve a list of Statement Setting records that should be processed on the current day.

        responses:
            200:
                description: A list of Statement Settings, filtered and ordered by the User
            403: {}
        """
        tracer = settings.TRACER

        with tracer.start_span('validating_controller', child_of=request.span) as span:
            controller = StatementSettingsListController(data=request.GET, request=request, span=span)
            # By validating the controller we generate the filters
            controller.is_valid()

        with tracer.start_span('setting_filters', child_of=request.span) as span:
            # This is a scheduled job for sending statements from all Addresses to all Addresses
            # Get all Users who are set up to send statements today. If it's the end of the month, e.g Feb 28th, get
            # the settings for later dates too, i.e. statements that should go out on the 30th of each month
            current = datetime.utcnow()
            days_current_month = calendar.monthrange(current.year, current.month)[1]
            if current.day == days_current_month:  # pragma: no cover
                # Create a range from the current day up to 31
                kw = {'day__overlap': list(range(current.day, 32))}
            else:  # pragma: no cover
                kw = {'day__contains': [current.day]}

            address_filtering: Optional[Q] = None
            if request.user.id != 1:
                address_filtering = address_filtering = Q(address_id=request.user.address['id'])

        with tracer.start_span('retrieve_requested_objects', child_of=request.span):
            order = controller.cleaned_data['order']
            try:
                objs = StatementSettings.objects.filter(
                    **controller.cleaned_data['search'],
                    **kw,
                )
                if address_filtering:
                    objs = objs.filter(address_filtering)

                objs.exclude(
                    **controller.cleaned_data['exclude'],
                ).order_by(
                    order,
                )
            except (ValueError, ValidationError):
                return Http400(error_code='financial_statement_settings_list_001')

        with tracer.start_span('gathering_metadata', child_of=request.span):
            total_records = objs.count()
            page = controller.cleaned_data['page']
            limit = controller.cleaned_data['limit']
            metadata = {
                'page': page,
                'limit': limit,
                'order': controller.cleaned_data['order'],
                'warnings': controller.warnings,
                'total_records': total_records,
            }
            # Handle pagination
            objs = objs[page * limit:(page + 1) * limit]

        with tracer.start_span('serializing_data', child_of=request.span):
            span.set_tag('num_objects', objs.count())
            data = StatementSettingsSerializer(instance=objs, many=True).data

        return Response({'content': data, '_metadata': metadata})


class StatementSettingsResource(APIView):
    """
    Handles methods regarding the Statement Setting record for the reuquesting user's address i.e. read, update
    """

    def get(self, request: Request, pk: int) -> Response:
        """
        summary: |
            Read the details of the Statement Setting record for the reuquesting user's address

        description: |
            Read the details of the Statement Setting record for the reuquesting user's address, if one does not
            exist, the record will be created and returned

        path_params:
            pk:
                description: The address id of the Statement Settings record to be retrieved
                type: integer

        responses:
            200:
                description: Statement Setting was read successfully
            403: {}
        """
        tracer = settings.TRACER

        with tracer.start_span('checking_permissions', child_of=request.span):
            err = Permissions.read(request, pk)
            if err is not None:
                return err

        with tracer.start_span('retrieving_requested_object', child_of=request.span):
            obj, c = StatementSettings.objects.get_or_create(address_id=pk)

        with tracer.start_span('serializing_data', child_of=request.span):
            data = StatementSettingsSerializer(instance=obj).data

        return Response({'content': data})

    def put(self, request: Request, pk: int, partial: bool = False) -> Response:
        """
        summary: |
            Update the details of the Statement Setting record for the reuquesting user's address

        description: |
            Update the details of the Statement Setting record for the reuquesting user's address, if one does not
            exist, the record will be created

        path_params:
            pk:
                description: The address id of the Statement Settings record to be updated
                type: integer

        responses:
            200:
                description: Statement Setting was updated successfully
            400: {}
            403: {}
        """
        tracer = settings.TRACER

        with tracer.start_span('checking_permissions', child_of=request.span):
            err = Permissions.update(request, pk)
            if err is not None:
                return err

        with tracer.start_span('validating_controller', child_of=request.span) as span:
            controller = StatementSettingsUpdateController(data=request.data, request=request, span=span)
            if not controller.is_valid():
                return Http400(errors=controller.errors)

        with tracer.start_span('set_address_id', child_of=request.span):
            obj = controller.instance
            obj.address_id = pk

        with tracer.start_span('saving_objects', child_of=request.span):
            controller.instance.save()

        with tracer.start_span('serializing_data', child_of=span):
            data = StatementSettingsSerializer(instance=controller.instance).data

        return Response({'content': data})

    def patch(self, request: Request, pk: int) -> Response:
        """
        Attempt to partially update of the Statement Setting record for the reuquesting user's address
        """
        return self.put(request, pk, True)
