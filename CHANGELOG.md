# CHANGELOG

## 4.0.0
Date: 2025-01-30

- CloudCIX Major release of Version 4
- CloudCIX Framework base incremented to Python 3.10
- CloudCIX Framework base incremented to Django 5.0.10

## 3.0.4
Date: 2024-11-12

- Bug Fix: journal_entry.create append names to obj and serialize this obj so details are available for Notifications.
- Enhansement: Use `db_lock` when saving Nominal Ledger obj for journal_entry and transaction_base

## 3.0.3
Date: 2024-11-04

- Enhancement: Select multiple days to send automated statements during a calendar month.

## 3.0.2
Date: 2024-07-03

- Bug Fix: Tidy up debug log statements from reportting application.

## 3.0.1
Date: 2024-06-25

- Bug Fix: Communication with reporting application in lagacyapi after deployment.


## 3.0.0
Date: 2024-06-21

- CloudCIX Major release of Version 3.
- CloudCIX Framework base incremented from Python 3.7 to Python 3.8

## 2.1.0
Date: 2024-02-07

- Improved `rtd` (Return of Trading Details) service to exclude UK transactions after the 2020-12-31.

## 2.0.0
Date: 2024-01-02

- Extended validation for ``lines`` in a transaction to ensure that the ``description`` in a ``line`` was not too long.

## 1.1.0
Date: 2022-05-25

- Implemented locking database to save a Nominal Ledger object to prevent the same tsn number for the transaction type 
  for an address being assigned by the trigger function `insert_nominal_ledger_tsn()`

## 1.0.14
Date: 2022-03-04

- Fixed bug in Debtor and Creditor Statement service where if a statement was read on day 30, transactions that 
  where 30 days old were double counted in the summary.

## 1.0.13
Date: 2021-09-23

- Added the following service:
  - `cloud_bill`

## 1.0.12
Date: 2021-06-11

- Added the following services:
  - `purchases_analysis`
  - `purchases_by_territory`
  - `sales_analysis`

## 1.0.11
Date: 2020-08-10

- Debtors and Creditors that have no outstanding balance will not be returned in the `debtor_ledger` or 
  `creditor_ledger` endpoints.

## 1.0.10
Date: 2020-08-05

- Updated template for Statement email notification.

## 1.0.9
Date: 2020-07-24

- Bug fixes in Purchases by Country and Sales by Country services

## 1.0.8 
Date: 2020-06-05

   - Increase the precision of the Nominal Ledger's `unit_price` field from 4 decimal places to 8 decimal places.
   - The RTD service now requries a `start_date` and `end_date` instead of a `year` parameter.

## 0.0.7
Date: 2020-04-23

-  Added the following transaction services that do no take a `contra_address_id`:
   - `cash_purchase_receipt`
   - `cash_purchase_refund`
   - `cash_sale_receipt`
   - `cash_sale_refund`

## 0.0.6
Date: 2020-03-10

-  Allow for an optional `tax_amount` to sent in the following services to allow a 0.02 difference to 
   (`unit_price` * `quantity` * `tax_rate__percent` / 100)
   - `cash_purchase_debit_note.create`
   - `cash_purchase_invoice.create`
   - `account_purchase_debit_note.create`
   - `account_purchase_invoice.create`
- The Notification Service will only send Notifications to current active Users.
- Removed functionality to notify Administrators about expired users in Notifications.

## 0.0.5
Date: 2020-03-04

- The Notification Service will send an email to Administrators if all users who are to recive the Notification
  have expired.
- Statement service is optimized to only get the details of trading partners who have recieved an Account Sale
  Invoice which has an unallocated balance.
- Email Log Serializer returns `created` timestamp in ISO format.
- Global Nominal Account Serializer returns `created` and `updated` timestamps in ISO format.

## 0.0.4
Date: 2020-03-03

- Bug fixes in Statement service

## 0.0.3
Date: 2020-02-28

- Bug fixes in notifications.py

## 0.0.2
Date: 2020-02-24

- Bug fixes in VAT3 report

## 0.0.1
Date: 2020-02-21

- Update adjustments to allow Users to select any Nominal Account in their Address, not just those for Sales or
  Purchases.
- When listing Nominal Accounts a User will see the Address Nominal Account data for whatever Address they are
  currently in.

## 0.0.0
Date: 2020-02-19

- Initial Release
