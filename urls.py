from django.urls import path
from . import views

urlpatterns = [
    # Account Purchase Adjustment
    path(
        'account_purchase_adjustment/',
        views.AccountPurchaseAdjustmentCollection.as_view(),
        name='account_purchase_adjustment_collection',
    ),
    path(
        'account_purchase_adjustment/<int:tsn>/',
        views.AccountPurchaseAdjustmentResource.as_view(),
        name='account_purchase_adjustment_resource',
    ),
    path(
        'account_purchase_adjustment_contra/address/<int:source_id>/',
        views.AccountPurchaseAdjustmentContraCollection.as_view(),
        name='account_purchase_adjustment_contra_collection',
    ),
    path(
        'account_purchase_adjustment_contra/address/<int:source_id>/<int:tsn>/',
        views.AccountPurchaseAdjustmentContraResource.as_view(),
        name='account_purchase_adjustment_contra_resource',
    ),

    # Account Purchase Debit Note
    path(
        'account_purchase_debit_note/',
        views.AccountPurchaseDebitNoteCollection.as_view(),
        name='account_purchase_debit_note_collection',
    ),
    path(
        'account_purchase_debit_note/<int:tsn>/',
        views.AccountPurchaseDebitNoteResource.as_view(),
        name='account_purchase_debit_note_resource',
    ),
    path(
        'account_purchase_debit_note_contra/address/<int:source_id>/',
        views.AccountPurchaseDebitNoteContraCollection.as_view(),
        name='account_purchase_debit_note_contra_collection',
    ),
    path(
        'account_purchase_debit_note_contra/address/<int:source_id>/<int:tsn>/',
        views.AccountPurchaseDebitNoteContraResource.as_view(),
        name='account_purchase_debit_note_contra_resource',
    ),

    # Account Purchase Invoice
    path(
        'account_purchase_invoice/',
        views.AccountPurchaseInvoiceCollection.as_view(),
        name='account_purchase_invoice_collection',
    ),
    path(
        'account_purchase_invoice/<int:tsn>/',
        views.AccountPurchaseInvoiceResource.as_view(),
        name='account_purchase_invoice_resource',
    ),
    path(
        'account_purchase_invoice_contra/address/<int:source_id>/',
        views.AccountPurchaseInvoiceContraCollection.as_view(),
        name='account_purchase_invoice_contra_collection',
    ),
    path(
        'account_purchase_invoice_contra/address/<int:source_id>/<int:tsn>/',
        views.AccountPurchaseInvoiceContraResource.as_view(),
        name='account_purchase_invoice_contra_resource',
    ),

    # Account Purchase Payment
    path(
        'account_purchase_payment/',
        views.AccountPurchasePaymentCollection.as_view(),
        name='account_purchase_payment_collection',
    ),
    path(
        'account_purchase_payment/<int:tsn>/',
        views.AccountPurchasePaymentResource.as_view(),
        name='account_purchase_payment_resource',
    ),
    path(
        'account_purchase_payment_contra/address/<int:source_id>/',
        views.AccountPurchasePaymentContraCollection.as_view(),
        name='account_purchase_payment_contra_collection',
    ),
    path(
        'account_purchase_payment_contra/address/<int:source_id>/<int:tsn>/',
        views.AccountPurchasePaymentContraResource.as_view(),
        name='account_purchase_payment_contra_resource',
    ),

    # Account Sale Adjustment
    path(
        'account_sale_adjustment/',
        views.AccountSaleAdjustmentCollection.as_view(),
        name='account_sale_adjustment_collection',
    ),
    path(
        'account_sale_adjustment/<int:tsn>/',
        views.AccountSaleAdjustmentResource.as_view(),
        name='account_sale_adjustment_resource',
    ),
    path(
        'account_sale_adjustment_contra/address/<int:source_id>/',
        views.AccountSaleAdjustmentContraCollection.as_view(),
        name='account_sale_adjustment_contra_collection',
    ),
    path(
        'account_sale_adjustment_contra/address/<int:source_id>/<int:tsn>/',
        views.AccountSaleAdjustmentContraResource.as_view(),
        name='account_sale_adjustment_contra_resource',
    ),

    # Account Sale Credit Note
    path(
        'account_sale_credit_note/',
        views.AccountSaleCreditNoteCollection.as_view(),
        name='account_sale_credit_note_collection',
    ),
    path(
        'account_sale_credit_note/<int:tsn>/',
        views.AccountSaleCreditNoteResource.as_view(),
        name='account_sale_credit_note_resource',
    ),
    path(
        'account_sale_credit_note_contra/address/<int:source_id>/',
        views.AccountSaleCreditNoteContraCollection.as_view(),
        name='account_sale_credit_note_contra_collection',
    ),
    path(
        'account_sale_credit_note_contra/address/<int:source_id>/<int:tsn>/',
        views.AccountSaleCreditNoteContraResource.as_view(),
        name='account_sale_credit_note_contra_resource',
    ),

    # Account Sale Invoice
    path(
        'account_sale_invoice/',
        views.AccountSaleInvoiceCollection.as_view(),
        name='account_sale_invoice_collection',
    ),
    path(
        'account_sale_invoice/<int:tsn>/',
        views.AccountSaleInvoiceResource.as_view(),
        name='account_sale_invoice_resource',
    ),
    path(
        'account_sale_invoice_contra/address/<int:source_id>/',
        views.AccountSaleInvoiceContraCollection.as_view(),
        name='account_sale_invoice_contra_collection',
    ),
    path(
        'account_sale_invoice_contra/address/<int:source_id>/<int:tsn>/',
        views.AccountSaleInvoiceContraResource.as_view(),
        name='account_sale_invoice_contra_resource',
    ),

    # Account Sale Payment
    path(
        'account_sale_payment/',
        views.AccountSalePaymentCollection.as_view(),
        name='account_sale_payment_collection',
    ),
    path(
        'account_sale_payment/<int:tsn>/',
        views.AccountSalePaymentResource.as_view(),
        name='account_sale_payment_resource',
    ),
    path(
        'account_sale_payment_contra/address/<int:source_id>/',
        views.AccountSalePaymentContraCollection.as_view(),
        name='account_sale_payment_contra_collection',
    ),
    path(
        'account_sale_payment_contra/address/<int:source_id>/<int:tsn>/',
        views.AccountSalePaymentContraResource.as_view(),
        name='account_sale_payment_contra_resource',
    ),

    # Allocation
    path(
        'allocation/',
        views.AllocationCollection.as_view(),
        name='allocation_collection',
    ),
    path(
        'allocation/<int:pk>/',
        views.AllocationResource.as_view(),
        name='allocation_resource',
    ),

    # Balance Sheet
    path(
        'balance_sheet/',
        views.BalanceSheetCollection.as_view(),
        name='balance_sheet_collection',
    ),

    # Cash Purchase Debit Note
    path(
        'cash_purchase_debit_note/',
        views.CashPurchaseDebitNoteCollection.as_view(),
        name='cash_purchase_debit_note_collection',
    ),
    path(
        'cash_purchase_debit_note/<int:tsn>/',
        views.CashPurchaseDebitNoteResource.as_view(),
        name='cash_purchase_debit_note_resource',
    ),
    path(
        'cash_purchase_debit_note_contra/address/<int:source_id>/',
        views.CashPurchaseDebitNoteContraCollection.as_view(),
        name='cash_purchase_debit_note_contra_collection',
    ),
    path(
        'cash_purchase_debit_note_contra/address/<int:source_id>/<int:tsn>/',
        views.CashPurchaseDebitNoteContraResource.as_view(),
        name='cash_purchase_debit_note_contra_resource',
    ),

    # Cash Purchase Invoice
    path(
        'cash_purchase_invoice/',
        views.CashPurchaseInvoiceCollection.as_view(),
        name='cash_purchase_invoice_collection',
    ),
    path(
        'cash_purchase_invoice/<int:tsn>/',
        views.CashPurchaseInvoiceResource.as_view(),
        name='cash_purchase_invoice_resource',
    ),
    path(
        'cash_purchase_invoice_contra/address/<int:source_id>/',
        views.CashPurchaseInvoiceContraCollection.as_view(),
        name='cash_purchase_invoice_contra_collection',
    ),
    path(
        'cash_purchase_invoice_contra/address/<int:source_id>/<int:tsn>/',
        views.CashPurchaseInvoiceContraResource.as_view(),
        name='cash_purchase_invoice_contra_resource',
    ),

    # Cash Purchase Receipt
    path(
        'cash_purchase_receipt/',
        views.CashPurchaseReceiptCollection.as_view(),
        name='cash_purchase_receipt_collection',
    ),
    path(
        'cash_purchase_receipt/<int:tsn>/',
        views.CashPurchaseReceiptResource.as_view(),
        name='cash_purchase_receipt_resource',
    ),

    # Cash Purchase Refund
    path(
        'cash_purchase_refund/',
        views.CashPurchaseRefundCollection.as_view(),
        name='cash_purchase_refund_collection',
    ),
    path(
        'cash_purchase_refund/<int:tsn>/',
        views.CashPurchaseRefundResource.as_view(),
        name='cash_purchase_refund_resource',
    ),

    # Cash Sale Credit Note
    path(
        'cash_sale_credit_note/',
        views.CashSaleCreditNoteCollection.as_view(),
        name='cash_sale_credit_note_collection',
    ),
    path(
        'cash_sale_credit_note/<int:tsn>/',
        views.CashSaleCreditNoteResource.as_view(),
        name='cash_sale_credit_note_resource',
    ),
    path(
        'cash_sale_credit_note_contra/address/<int:source_id>/',
        views.CashSaleCreditNoteContraCollection.as_view(),
        name='cash_sale_credit_note_contra_collection',
    ),
    path(
        'cash_sale_credit_note_contra/address/<int:source_id>/<int:tsn>/',
        views.CashSaleCreditNoteContraResource.as_view(),
        name='cash_sale_credit_note_contra_resource',
    ),

    # Cash Sale Invoice
    path(
        'cash_sale_invoice/',
        views.CashSaleInvoiceCollection.as_view(),
        name='cash_sale_invoice_collection',
    ),
    path(
        'cash_sale_invoice/<int:tsn>/',
        views.CashSaleInvoiceResource.as_view(),
        name='cash_sale_invoice_resource',
    ),
    path(
        'cash_sale_invoice_contra/address/<int:source_id>/',
        views.CashSaleInvoiceContraCollection.as_view(),
        name='cash_sale_invoice_contra_collection',
    ),
    path(
        'cash_sale_invoice_contra/address/<int:source_id>/<int:tsn>/',
        views.CashSaleInvoiceContraResource.as_view(),
        name='cash_sale_invoice_contra_resource',
    ),

    # Cash Sale Receipt
    path(
        'cash_sale_receipt/',
        views.CashSaleReceiptCollection.as_view(),
        name='cash_sale_receipt_collection',
    ),
    path(
        'cash_sale_receipt/<int:tsn>/',
        views.CashSaleReceiptResource.as_view(),
        name='cash_sale_receipt_resource',
    ),

    # Cash Sale Refund
    path(
        'cash_sale_refund/',
        views.CashSaleRefundCollection.as_view(),
        name='cash_sale_refund_collection',
    ),
    path(
        'cash_sale_refund/<int:tsn>/',
        views.CashSaleRefundResource.as_view(),
        name='cash_sale_refund_resource',
    ),

    # Cloud Bill
    path(
        'cloud_bill/<int:project_id>/',
        views.CloudbillResource.as_view(),
        name='cloud_bill',
    ),

    # Credit Limit
    path(
        'credit_limit/',
        views.CreditLimitCollection.as_view(),
        name='credit_limit_collection',
    ),
    path(
        'credit_limit/<int:address_id>/',
        views.CreditLimitResource.as_view(),
        name='credit_limit_resource',
    ),

    # Creditor Account
    path(
        'creditor_account/<int:id>/history/',
        views.CreditorAccountHistoryCollection.as_view(),
        name='creditor_account_history',
    ),
    path(
        'creditor_account/<int:id>/statement/',
        views.CreditorAccountStatementCollection.as_view(),
        name='creditor_account_statement',
    ),

    # Creditor Ledger
    path(
        'creditor_ledger/',
        views.CreditorLedgerCollection.as_view(),
        name='creditor_ledger_collection',
    ),
    path(
        'creditor_ledger/aged/',
        views.CreditorLedgerAgedCollection.as_view(),
        name='creditor_ledger_aged_collection',
    ),
    path(
        'creditor_ledger/transaction/',
        views.CreditorLedgerTransactionCollection.as_view(),
        name='creditor_ledger_transaction_collection',
    ),
    path(
        'creditor_ledger/contra_transaction/',
        views.CreditorLedgerContraTransactionCollection.as_view(),
        name='creditor_ledger_contra_transaction_collection',
    ),

    # Debtor Account
    path(
        'debtor_account/<int:id>/history/',
        views.DebtorAccountHistoryCollection.as_view(),
        name='debtor_account_history',
    ),
    path(
        'debtor_account/<int:id>/statement/',
        views.DebtorAccountStatementCollection.as_view(),
        name='debtor_account_statement',
    ),

    # Debtor Ledger
    path(
        'debtor_ledger/',
        views.DebtorLedgerCollection.as_view(),
        name='debtor_ledger_collection',
    ),
    path(
        'debtor_ledger/aged/',
        views.DebtorLedgerAgedCollection.as_view(),
        name='debtor_ledger_aged_collection',
    ),
    path(
        'debtor_ledger/transaction/',
        views.DebtorLedgerTransactionCollection.as_view(),
        name='debtor_ledger_transaction_collection',
    ),
    path(
        'debtor_ledger/contra_transaction/',
        views.DebtorLedgerContraTransactionCollection.as_view(),
        name='debtor_ledger_contra_transaction_collection',
    ),

    # Global Nominal Account
    path(
        'global_nominal_account/',
        views.GlobalNominalAccountCollection.as_view(),
        name='global_nominal_account_collection',
    ),
    path(
        'global_nominal_account/<int:pk>/',
        views.GlobalNominalAccountResource.as_view(),
        name='global_nominal_account_resource',
    ),

    # Journal Entry
    path(
        'journal_entry/',
        views.JournalEntryCollection.as_view(),
        name='journal_entry_collection',
    ),
    path(
        'journal_entry/<int:tsn>/',
        views.JournalEntryResource.as_view(),
        name='journal_entry_resource',
    ),

    # Nominal Account History
    path(
        'nominal_account/<int:id>/history/',
        views.NominalAccountHistoryCollection.as_view(),
        name='nominal_account_history',
    ),

    # Nominal Account Type
    path(
        'nominal_account_type/',
        views.NominalAccountTypeCollection.as_view(),
        name='nominal_account_type_collection',
    ),

    # Nominal Contra
    path(
        'nominal_contra/',
        views.NominalContraCollection.as_view(),
        name='nominal_contra_collection',
    ),
    path(
        'nominal_contra/<int:pk>/',
        views.NominalContraResource.as_view(),
        name='nominal_contra_resource',
    ),

    # Payment Method
    path(
        'payment_method/',
        views.PaymentMethodCollection.as_view(),
        name='payment_method_collection',
    ),
    path(
        'payment_method/<int:pk>/',
        views.PaymentMethodResource.as_view(),
        name='payment_method_resource',
    ),

    # Period End
    path(
        'period_end/',
        views.PeriodEndCollection.as_view(),
        name='period_end_collection',
    ),
    path(
        'period_end/<int:tsn>/',
        views.PeriodEndResource.as_view(),
        name='period_end_resource',
    ),

    # Profit and Loss
    path(
        'profit_and_loss/',
        views.ProfitAndLossCollection.as_view(),
        name='profit_and_loss_collection',
    ),

    # Purchases Analysis
    path(
        'purchases_analysis/',
        views.PurchasesAnalysisCollection.as_view(),
        name='purchases_analysis_collection',
    ),

    # Purchase by Country
    path(
        'purchases_by_country/',
        views.PurchasesByCountryCollection.as_view(),
        name='purchases_by_country_collection',
    ),

    # Purchases by Territory
    path(
        'purchases_by_territory/<int:territory_id>/',
        views.PurchasesByTerritoryCollection.as_view(),
        name='purchases_by_territory_collection',
    ),

    # RTD (Return of Trading Details)
    path(
        'rtd/',
        views.RTDCollection.as_view(),
        name='rtd_collection',
    ),

    # Sales Analysis
    path(
        'sales_analysis/',
        views.SalesAnalysisCollection.as_view(),
        name='sales_analysis_collection',
    ),

    # Sales by Country
    path(
        'sales_by_country/',
        views.SalesByCountryCollection.as_view(),
        name='sales_by_country_collection',
    ),

    # Sales by Territory
    path(
        'sales_by_territory/<int:territory_id>/',
        views.SalesByTerritoryCollection.as_view(),
        name='sales_by_territory_collection',
    ),

    path(
        'statement/',
        views.StatementCollection.as_view(),
        name='statement_collection',
    ),

    # Statement Log
    path(
        'statement_log/',
        views.StatementLogCollection.as_view(),
        name='statement_log_collection',
    ),

    # Statement Settings
    path(
        'statement_settings/',
        views.StatementSettingsCollection.as_view(),
        name='statement_settings_collection',
    ),
    path(
        'statement_settings/<int:pk>/',
        views.StatementSettingsResource.as_view(),
        name='statement_settings_resource',
    ),

    # Tax Rate
    path(
        'tax_rate/',
        views.TaxRateCollection.as_view(),
        name='tax_rate_collection',
    ),
    path(
        'tax_rate/<int:pk>/',
        views.TaxRateResource.as_view(),
        name='tax_rate_resource',
    ),

    # Trial Balance
    path(
        'trial_balance/',
        views.TrialBalanceCollection.as_view(),
        name='trial_balance_collection',
    ),

    # VAT 3
    path(
        'vat3/',
        views.VAT3Collection.as_view(),
        name='vat3_collection',
    ),

    # Vies
    path(
        'vies_purchases/',
        views.VIESPurchasesCollection.as_view(),
        name='vies_purchases_collection',
    ),

    path(
        'vies_sales/',
        views.VIESSalesCollection.as_view(),
        name='vies_sales_collection',
    ),

    # Year End
    path(
        'year_end/',
        views.YearEndCollection.as_view(),
        name='year_end_collection',
    ),
    path(
        'year_end/<int:tsn>/',
        views.YearEndResource.as_view(),
        name='year_end_resource',
    ),
]
