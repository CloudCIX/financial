from ..models import (
    GlobalNominalAccount,
    NominalContra,
    PaymentMethod,
    StatementSettings,
    TaxRate,
)


def financial_setup(request):
    """
    summary:  |
        This function checks and creates the default Financial records required for a Member to start using Financials

    description: |
        1. Create default Global Nominal Accounts
        - description: Petty Cash; nominal_account_number: 1000; valid_purchases_account: False;
        valid_sales_account: False;
        - description: Curent Account; nominal_account_number: 1010; valid_purchases_account: False;
        valid_sales_account: False;
        - description: Debtors Control Account; nominal_account_number: 1300; valid_purchases_account: False;
        valid_sales_account: False;
        - description: Creditors Control Account; nominal_account_number: 2200; valid_purchases_account: False;
        valid_sales_account: False;
        - description: Vat Control Account; nominal_account_number: 2210; valid_purchases_account: False;
        valid_sales_account: False;
        - description: Profit and Loss b/f; nominal_account_number: 3500; valid_purchases_account: False;
        valid_sales_account: False;
        - description: Sales Account; nominal_account_number: 4000; valid_purchases_account: False;
        valid_sales_account: True;
        - description: Purchases Account; nominal_account_number 5000; valid_purchases_account: True;
        valid_sales_account: False;
        - description: Direct Expenses; nominal_account_number: 6000; valid_purchases_account: False;
        valid_sales_account: False;
        - description: Sundry Expemses; nominal_account_number: 6900; valid_purchases_account: False;
        valid_sales_account: False;
        - description: Suspence Account; nominal_account_number: 7999; valid_purchases_account: False;
        valid_sales_account: False;

        2. Create default Payment Methods
        - description: Cash
        - description: Transfer

        3. Create default Nominal Contra Accounts
        - global_nominal_account: Petty Cash; payment_method: Cash; transaction_type_id: 10000(Cash Purchase Invoice)
        - global_nominal_account: Petty Cash; payment_method: Cash; transaction_type_id: 10001(Cash Purchase Debit Note)
        - global_nominal_account: Curent Account; payment_method: Transfer;
        transaction_type_id: 10004(Account Purchase Payment)
        - global_nominal_account: Petty Cash; payment_method: Cash; transaction_type_id: 11000(Cash Sales Invoice)
        - global_nominal_account: Petty Cash; payment_method: Cash; transaction_type_id: 11001(Cash Sales Credit Note)
        - global_nominal_account: Curent Account; payment_method: Transfer;
        transaction_type_id: 11004(Account Sale Payment)

        4. Create default Tax Rates
        - description: Exempt; percent:0
        - description: Zero Rate Export; percent:0
        - description: Zero Rate Home; percent:0
        - description: Livestock Rate; percent:4.8
        - description: Flat-Rate Addition; percent:5.4
        - description: Second Reduced Rate; percent:9
        - description: Reduced Rate; percent:13.5
        - description: Standard Rate; percent:23
    """
    statement = StatementSettings.objects.filter(address_id=request.user.address['id'])
    global_nominal_accounts = GlobalNominalAccount.objects.filter(member_id=request.user.member['id'])
    payment_methods = PaymentMethod.objects.filter(member_id=request.user.member['id'])
    tax_rates = TaxRate.objects.filter(address_id=request.user.address['id'])

    # If a statement record for the requesting users address does not exist, one must be created
    if statement.count() == 0:
        StatementSettings.objects.create(address_id=request.user.address['id'])

    # If no records exist for the global nominal accounts, payment records and tax_rate for requesting user's
    # Member or Address, default records must be created
    if global_nominal_accounts.count() == 0 and payment_methods.count() == 0 and tax_rates.count() == 0:
        # Global Nominal Accounts
        default_accounts = GlobalNominalAccount.objects.filter(member_id=0)

        for account in default_accounts:
            GlobalNominalAccount.objects.create(
                currency_id=request.user.member['currency_id'],
                description=account.description,
                external_reference=account.external_reference,
                member_id=request.user.member['id'],
                nominal_account_number=account.nominal_account_number,
                nominal_account_type=account.nominal_account_type,
                valid_purchases_account=account.valid_purchases_account,
                valid_sales_account=account.valid_sales_account,
            )
        # If no records exist for the payments method for requesting user's Member, default records must be created
        # Payment Methods
        default_payment_methods = PaymentMethod.objects.filter(member_id=0)
        for payment_method in default_payment_methods:
            PaymentMethod.objects.create(
                description=payment_method.description,
                member_id=request.user.member['id'],
            )
        # Nominal Contras
        default_contras = NominalContra.objects.filter(
            global_nominal_account__member_id=0,
            payment_method__member_id=0,
        )
        # if no records exist for either global nominal account or payment methods for the requesting user's member then
        # the default nominal contra records need to be created
        for contra in default_contras:
            try:
                account = GlobalNominalAccount.objects.get(
                    member_id=request.user.member['id'],
                    nominal_account_number=contra.global_nominal_account.nominal_account_number,
                )
                payment_method = PaymentMethod.objects.get(
                    deleted__isnull=True,
                    member_id=request.user.member['id'],
                    description=contra.payment_method.description,
                )
            except (GlobalNominalAccount.DoesNotExist, PaymentMethod.DoesNotExist):  # pragma: no cover
                pass
            try:
                NominalContra.objects.get(
                    global_nominal_account=account,
                    payment_method=payment_method,
                    transaction_type_id=contra.transaction_type_id,
                )
            except NominalContra.DoesNotExist:
                NominalContra.objects.create(
                    global_nominal_account=account,
                    payment_method=payment_method,
                    transaction_type_id=contra.transaction_type_id,
                )

        # Tax Rates
        default_tax_rates = TaxRate.objects.filter(address_id=0)
        for tax_rate in default_tax_rates:
            TaxRate.objects.create(
                address_id=request.user.address['id'],
                percent=tax_rate.percent,
                description=tax_rate.description,
            )
