from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('financial', '0008_django5'),
    ]

    operations = [
        migrations.RunSQL("""
            -------------------------------------------------------------
            -- View used to get the Nominal Accounts and their balance --
            -------------------------------------------------------------
            -- It would be preferable to find a way to do this using the Django ORM instead

            CREATE OR REPLACE VIEW "nominal_account_history"
            AS
            SELECT
                "address_id", "contra_address_id", "tsn", "transaction_type_id", "transaction_date", "narrative",
                "name_bill_to", "id" AS nominal_ledger_id, "nominal_account_number", SUM(amount) AS amount,
                ROW_NUMBER() OVER() AS id
            FROM
            (
                SELECT
                    "address_id", "contra_address_id", "tsn", "transaction_type_id", "transaction_date", "narrative",
                    "name_bill_to", NL."id", "nominal_account_number", SUM("amount") * -1 AS amount
                FROM "nominal_ledger" as NL
                INNER JOIN "nominal_ledger_credits" as NLC
                ON NL."id" = NLC."nominal_ledger_id"
                WHERE NL."deleted" IS NULL AND NLC."deleted" IS NULL
                GROUP BY
                    "address_id", "contra_address_id", "tsn", "transaction_type_id", "transaction_date", "narrative",
                    "name_bill_to", NL."id", "nominal_account_number"

                UNION ALL
                SELECT
                    "address_id", "contra_address_id", "tsn", "transaction_type_id", "transaction_date", "narrative",
                    "name_bill_to", NL."id", "nominal_account_number", SUM("amount") AS amount
                FROM "nominal_ledger" as NL
                INNER JOIN "nominal_ledger_debits" as NLD
                ON NL."id" = NLD."nominal_ledger_id"
                WHERE NL."deleted" IS NULL AND NLD."deleted" IS NULL
                GROUP BY
                     "address_id", "contra_address_id", "tsn", "transaction_type_id", "transaction_date", "narrative",
                    "name_bill_to", NL."id", "nominal_account_number"
            ) t
            GROUP BY
                "address_id", "contra_address_id", "tsn", "transaction_type_id", "transaction_date", "narrative",
                "name_bill_to", "id", "nominal_account_number";
        """),

        # ############################################################################## #
        #    Calculate the unallocated balance for an id_nominal_ledger (BigAutoField)   #
        # ############################################################################## #
        migrations.RunSQL("""
            CREATE OR REPLACE FUNCTION get_unallocated_balance(id_nominal_ledger bigint)
                RETURNS decimal(23,4) AS
            $BODY$
            DECLARE
                unallocated_balance decimal(23, 4);
            BEGIN
                SELECT COALESCE(SUM(total), 0) INTO unallocated_balance
                FROM (SELECT COALESCE(nominal_ledger_debits.amount, 0) AS total
                FROM nominal_ledger_debits
                WHERE nominal_ledger_id = id_nominal_ledger
                    AND nominal_account_number IN (1300, 2200)
                    AND deleted IS NULL
                UNION ALL
                SELECT COALESCE(nominal_ledger_credits.amount, 0) * -1 AS total
                FROM nominal_ledger_credits
                WHERE nominal_ledger_id = id_nominal_ledger
                    AND nominal_account_number IN (1300, 2200)
                    AND deleted IS NULL
                UNION ALL
                SELECT COALESCE(SUM(debit_amount), 0) + COALESCE(SUM(credit_amount), 0) AS total
                FROM allocation_detail
                WHERE nominal_ledger_id = id_nominal_ledger AND deleted IS NULL) t;
                RETURN unallocated_balance;
            END
            $BODY$
                LANGUAGE plpgsql VOLATILE
                COST 100;
        """),
    ]
