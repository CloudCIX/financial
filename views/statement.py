"""
Management for Statements
This service aggregates data from the Nominal Ledger and sends it in an email to a User's debtors
It creates Statement Log records
"""

# stdlib
import requests
import time
from collections import deque
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Deque, Dict, List, Set, Tuple
# libs
from cloudcix.api.membership import Membership
from cloudcix.api.reporting import Reporting
from cloudcix_rest.exceptions import Http400
from cloudcix_rest.views import APIView
from django.conf import settings
from django.core.mail import EmailMultiAlternatives, get_connection
from django.db.models import Q, Sum
from django.template.loader import render_to_string
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
# local
from financial.controllers import StatementCreateController
from financial.models import NominalLedger, StatementLog, StatementSettings
from financial.serializers import NominalLedgerSerializer


__all__ = [
    'StatementCollection',
]


class StatementCollection(APIView):
    """
    Handles methods regarding Nominal Ledger records that don't require an id to be specified
    """

    def post(self, request: Request):
        """
        summary: Send an email of unallocated transactions to an Address' debtors

        description: |
            Generate a report of unallocated sale transactions between the validate accounts `address_id` and
            debtor's `contra_address_id`.
            Email the report to each User in their debtor's Addresses

        responses:
            204:
                description: Statements were sent successfully. No data is returned in the response
            400: {}
        """
        tracer = settings.TRACER

        with tracer.start_span('validating_controller', child_of=request.span) as span:
            controller = StatementCreateController(data=request.data, request=request, span=span)
            if not controller.is_valid():
                return Http400(errors=controller.errors)
            address_id = controller.cleaned_data.get('address_id')
            contra_address_id = controller.cleaned_data.get('contra_address_id')

        with tracer.start_span('existing_sale_trading_partner', child_of=request.span):
            # There are no account sales invoices issued by the address_id to the contra_address_id for a Statement
            ledger_objs = NominalLedger.account_sale_invoices.filter(
                address_id=address_id,
                contra_address_id=contra_address_id,
            )
            if ledger_objs.exists() is False:
                # There are no sale transactions between the two addresses, no need for log record
                return Response(status=status.HTTP_204_NO_CONTENT)

        with tracer.start_span('unallocated_balance_between_addresses', child_of=request.span):
            if ledger_objs.exclude(unallocated_balance=Decimal('0')).exists() is False:
                StatementLog.objects.create(
                    address_id=address_id,
                    contra_address_id=contra_address_id,
                    comment='There are no Account Sale Invoices with an unallocated balance to generate a statement.',
                    status='skipped',
                )
                return Response(status=status.HTTP_204_NO_CONTENT)

        with tracer.start_span('statement_sent_today', child_of=request.span):
            # A successful statement was processed today from the address_id to the contra_address_id.
            # We do not want to send multiple statements for the same addresses in one day.
            if StatementLog.objects.filter(
                created__gte=datetime.utcnow().date(),
                address_id=address_id,
                contra_address_id=contra_address_id,
            ).exclude(
                status__in=['skipped', 'error'],
            ).exists():
                return Response(status=status.HTTP_204_NO_CONTENT)

        with tracer.start_span('fetching_mailing_list', child_of=request.span):
            mailing_list = self.get_mailing_list(request.user.token, contra_address_id)

            if len(mailing_list) == 0:  # pragma: no cover
                # No User in contra_address_id set up to recieve Sale transaction notifications
                StatementLog.objects.create(
                    address_id=address_id,
                    contra_address_id=contra_address_id,
                    comment='No User set up to recieve Sale transaction notifications.',
                    status='skipped',
                )
                return Response(status=status.HTTP_204_NO_CONTENT)

        with tracer.start_span('gathering_report_data', child_of=request.span):
            data, err = self.generate_report_data(request.user.token, address_id, contra_address_id)
            if err != '':
                # Log Reason Statement could not be sent
                StatementLog.objects.create(
                    address_id=address_id,
                    contra_address_id=contra_address_id,
                    comment=err,
                    status='skipped',
                )
                return Response(status=status.HTTP_204_NO_CONTENT)
                # Get the details of the Address and Contra Address

        with tracer.start_span('generating_report', child_of=request.span):
            response, err = self.generate_report(request.user.token, data)
            if err != '':  # pragma: no cover
                StatementLog.objects.create(
                    address_id=address_id,
                    contra_address_id=contra_address_id,
                    comment=err,
                    status='error',
                )
                return Response(status=status.HTTP_204_NO_CONTENT)
            response.raw.decode_content = True
            statement = response.content

        with tracer.start_span('sending_emails', child_of=request.span):
            # Create the emails
            emails: Deque = deque()
            recipients = list()
            for user in mailing_list:
                emails.append(self.write_email(user, data['address'], statement))
                recipients.append(user['first_name'] + ' ' + user['surname'])
                if not settings.PRODUCTION_DEPLOYMENT:
                    break

            # Send the emails
            if len(emails) > 0 and not settings.TESTING:  # pragma: no cover
                mail_backend = get_connection()
                mail_backend.send_messages(emails)

            msg = f'{len(emails)} email(s) sent to: ' + ', '.join(recipients)
            StatementLog.objects.create(
                address_id=address_id,
                contra_address_id=contra_address_id,
                comment=msg,
                status='success',
            )

        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_mailing_list(self, token: str, contra_address_id: int) -> List[Dict]:
        """
        Get a list of Users from the Contra Address who are set up to receive notifications.
        :param contra_address_id: The Address where the Users are from
        :return: A list of Users from Membership
        """
        users: Deque = deque()
        user_ids: Set[int] = set()

        for transaction_type_id in range(11000, 11006):
            params = {'page': 0, 'limit': 100}
            response = Membership.notification.list(
                token=token,
                pk=transaction_type_id,
                address_id=contra_address_id,
                params=params,
            )
            content = response.json()['content']
            total_records = response.json()['_metadata']['total_records']
            while len(content) < total_records:  # pragma: no cover
                params['page'] += 1
                response = Membership.notification.list(
                    token=token,
                    pk=transaction_type_id,
                    address_id=contra_address_id,
                    params=params,
                )
                content.extend(response.json()['content'])

            for user in content:
                if user['id'] in user_ids:
                    # Don't send multiple emails to the same user
                    continue
                users.append(user)
                user_ids.add(user['id'])

        return list(users)

    def generate_report_data(self, token: str, address_id: int, contra_address_id: int) -> Tuple[Dict, str]:
        """
        Get all the data required to populate the report template
        :param token: The requesting User's token
        :param address_id: The id of an Address who is sending statements
        :param contra_address_id: The id of an Address who is receiving the statement
        :return: A dictionary containing values for populating a statement template
        """
        search_params = {
            'address_id': address_id,
            'contra_address_id': contra_address_id,
            'transaction_type_id__range': (11000, 11005),
        }

        objs = NominalLedger.objects.exclude(
            unallocated_balance=Decimal('0'),
        ).filter(
            **search_params,
        ).order_by(
            'transaction_date',
            'id',
        )
        total_records = objs.count()
        data = NominalLedgerSerializer(instance=objs, many=True).data
        running_balance = Decimal('0')
        # For each individual Ledger entry, we want to sum up the unallocated balances of the Ledger entries before it
        for ledger in data:
            running_balance += Decimal(ledger['unallocated_balance'])
            ledger['running_balance'] = running_balance

        metadata = self.gather_metadata(search_params)
        statement_settings = StatementSettings.objects.get(address_id=address_id)

        # Check if the Address wants to send a statements to this Contra Address
        current_balance = Decimal(metadata['current_balance'])
        if current_balance < 0:  # pragma: no cover
            min_credit = Decimal(getattr(statement_settings, 'min_credit', '0'))
            if min_credit < current_balance:
                return {}, 'The balance does not exceed the minimum credit amount'
        elif current_balance > 0:  # pragma: no cover
            min_debit = Decimal(getattr(statement_settings, 'min_debit', '0'))
            if current_balance < min_debit:
                return {}, 'The balance does not exceed the minimum debit amount'
        else:  # pragma: no cover
            return {}, 'There is no balance on this account'

        # Get the details of the Address and Contra Address
        address = Membership.address.read(token=token, pk=address_id).json()['content']
        contra_address = Membership.address.read(token=token, pk=contra_address_id).json()['content']

        data = {
            'address': address,
            'contra_address': contra_address,
            'date': str(datetime.today().date()),
            'total_records': total_records,
            'transactions': data,
            **metadata,
        }

        return data, ''

    def gather_metadata(self, search_parameters: Dict) -> Dict:
        """
        Calculate the unallocated balance for a set of Nominal Ledger records, grouped by date ranges
        :param search_parameters: A dictionary used to filter Nominal Ledger records
        :return: A dictionary of balances for different date ranges
        """
        today = datetime.utcnow()
        day30 = today.date() - timedelta(days=30)
        day60 = day30 - timedelta(days=30)
        day90 = day60 - timedelta(days=30)

        objs = NominalLedger.objects.exclude(
            unallocated_balance=Decimal('0'),
        ).filter(
            **search_parameters,
        ).aggregate(
            balance_30_day=Sum(
                'unallocated_balance',
                filter=Q(transaction_date__gt=day30, transaction_date__lte=today),
            ),
            balance_60_day=Sum(
                'unallocated_balance',
                filter=Q(transaction_date__gt=day60, transaction_date__lte=day30),
            ),
            balance_90_day=Sum(
                'unallocated_balance',
                filter=Q(transaction_date__gt=day90, transaction_date__lte=day60),
            ),
            older_balance=Sum('unallocated_balance', filter=Q(transaction_date__lte=day90)),
        )

        # Calculate the `current_balance` and convert the balances to strings
        current_balance = Decimal('0')
        for k, v in objs.items():
            v = v if v is not None else Decimal('0')
            current_balance += v
            objs[k] = str(v)
        objs['current_balance'] = str(current_balance)

        return objs

    def generate_report(self, token: str, report_data: Dict) -> Tuple[requests.Response, str]:
        """
        Use the CloudCix Reporting engine to generate a pdf report of the sales statement
        :param token: The requesting User's token
        :param report_data: The data to populate the report
        :return: A response object with any error that may have occurred generating the statement
        """
        filename = '-'.join((report_data['date'], 'sale_statement'))
        report_content = {
            'data': report_data,
            'idReportTemplate': 58,
            'format': 'pdf',
            'name': filename,
        }

        response = Reporting.report.create(
            token=token,
            data=report_content,
            params={'fields': 'global_id'},
        )
        if response.status_code != 201:  # pragma: no cover
            error_msg = f'Report could not be generated. Response from Reporting: {response.json()["errors"]}'
            return response, error_msg
        global_id = response.json()['content']['global_id']

        # Wait for the report to be generated.
        err_msg = ''
        for _ in range(4):
            time.sleep(3)
            response = Reporting.report.read(
                token=token,
                pk=global_id,
                params={'fields': '(status,downloadLink,statusMessage)'},
            )
            if response.status_code != 200:  # pragma: no cover
                err_msg = 'Could not read report.'
                break
            content = response.json()['content']
            status = content['status']
            # If the response is a 200 and the status is 'working' or 'manual', stay in the loop
            if status not in ['working', 'manual']:
                break
        if err_msg != '':  # pragma: no cover
            return response, err_msg

        # Download the report so that it can be attached to emails
        download_url = settings.CLOUDCIX_API_URL + content['downloadLink']
        response = requests.get(download_url, stream=True, headers={'X-Auth-Token': token}, timeout=120)
        if response.status_code != 200:  # pragma: no cover
            return response, 'Report could not be downloaded'

        return response, ''

    def write_email(self, user: Dict, address: Dict, statement: bytes) -> EmailMultiAlternatives:
        """
        Given a statement, create an email that will be sent to a User
        :param user: A dict of User data
        :param address: A dict of Address data
        :param statement: A pdf of a sales statement
        :return: An email object
        """
        statement_settings = StatementSettings.objects.get(address_id=address['id'])
        if settings.PRODUCTION_DEPLOYMENT:  # pragma: no cover
            recipient = [f'{user["first_name"]} {user["surname"]} <{user["username"]}>']
            subject = 'Statement of Account'
        else:
            recipient = ['developers@cloudcix.com']
            subject = '[DEV] Statement of Account'
        message = render_to_string(
            'financial/email/statement_notification.txt',
            {
                'user': user,
                'address': address,
                'reply_to': statement_settings.reply_to,
                'signature': statement_settings.signature.replace('<br>', '\n').replace('<br />', '\n'),
            },
        )
        reply_to = statement_settings.reply_to or 'no-reply@cloudcix.com'
        email = EmailMultiAlternatives(
            from_email=settings.EMAIL_HOST_USER,
            to=recipient,
            bcc=settings.BCC_INVOICE_EMAILS,
            subject=subject,
            body=message,
            headers={'Reply-to': reply_to},
        )
        filename = str(datetime.utcnow().date()) + '-sale_statement.pdf'
        email.attach(filename, statement, 'application/pdf')

        html_message = render_to_string(
            'financial/email/statement_notification.html',
            {
                'user': user,
                'address': address,
                'reply_to': statement_settings.reply_to,
                'signature': statement_settings.signature,
            },
        )
        email.attach_alternative(html_message, 'text/html')

        return email
