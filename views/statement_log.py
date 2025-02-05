"""
Management for Statement Logs
"""

# libs
from cloudcix_rest.exceptions import Http400
from cloudcix_rest.views import APIView
from django.conf import settings
from django.core.exceptions import ValidationError
from rest_framework.request import Request
from rest_framework.response import Response
# local
from financial.controllers.statement_log import StatementLogListController
from financial.models.statement_log import StatementLog
from financial.serializers.statement_log import StatementLogSerializer


__all__ = [
    'StatementLogCollection',
]


class StatementLogCollection(APIView):
    """
    Handles methods regarding Statement Logs that don't require an id to be specified i.e. list
    """

    def get(self, request: Request) -> Response:
        """
        summary: Retrieve a list of Statement Log records

        description: Retrieve a list of Statement Log records that were sent by the requesting User's Address

        responses:
            200:
                description: A list of Statement Logs, filtered and ordered by the User
            400: {}
        """
        tracer = settings.TRACER

        with tracer.start_span('validating_controller', child_of=request.span) as span:
            controller = StatementLogListController(data=request.GET, request=request, span=span)
            # By validating the controller we generate the filters
            controller.is_valid()

        with tracer.start_span('retrieve_requested_objects', child_of=request.span):
            order = controller.cleaned_data['order']
            try:
                objs = StatementLog.objects.filter(
                    address_id=request.user.address['id'],
                    **controller.cleaned_data['search'],
                ).exclude(
                    **controller.cleaned_data['exclude'],
                ).order_by(
                    order,
                )
            except (ValueError, ValidationError):
                return Http400(error_code='financial_statement_log_list_001')

        with tracer.start_span('gathering_metadata', child_of=request.span):
            page = controller.cleaned_data['page']
            limit = controller.cleaned_data['limit']
            total_records = objs.count()
            # Handle Pagination
            objs = objs[page * limit: (page + 1) * limit]
            # Generate metadata
            metadata = {
                'page': page,
                'limit': limit,
                'order': order,
                'warnings': controller.warnings,
                'total_records': total_records,
            }

        with tracer.start_span('serializing_data', child_of=request.span) as span:
            span.set_tag('num_objects', objs.count())
            data = StatementLogSerializer(instance=objs, many=True).data

        return Response({'content': data, '_metadata': metadata})
