from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('financial', '0002_triggers'),
    ]

    operations = [
        # ------------------------------------------------------------------------------------------------------------ #
        #                               Function used to run the Integrity Test                                        #
        # ------------------------------------------------------------------------------------------------------------ #
        migrations.RunSQL("""
            CREATE OR REPLACE FUNCTION database_integrity_test_financial()
              RETURNS integer AS
            $BODY$
            -----------------------------------------------------------------------------------------------------------
            --                                            Functionality                                              --
            -----------------------------------------------------------------------------------------------------------
            -- This stored procedures runs an integrity test on the financial database.                              --
            -- Will run test and send details to IntegrityTest table.                                                --
            -- If error occurs will it send details to IntegrityTest table.                                          --
            -----------------------------------------------------------------------------------------------------------
            --                                               Methodology                                             --
            -----------------------------------------------------------------------------------------------------------
            -- Step 1  Check nominal_ledger Balance.                                                                 --
            -- Step 2  Check nominal_ledger Rounding.                                                                --
            -- Step 3  Check if transaction_sequence_number is unique.                                               --
            -- Step 4  Check Purchases debits and credits for rounding issues.                                       --
            -- Step 5  Check Period End balances.                                                                    --
            -----------------------------------------------------------------------------------------------------------
            --                                         Revision History                                              --
            -----------------------------------------------------------------------------------------------------------
            -- | Date     | Ticket | Developer   | Tester  | Justification                                            |
            -----------------------------------------------------------------------------------------------------------
            -- | 30/01/13 |  256   | Ray Moloney |         | Database Integrity Test                                  |
            -- | 12/02/13 |  266   | Ray Moloney |         | Add 010-077-001-003                                      |
            -- | 11/03/13 |  267   | Ray Moloney |         | Add 010-077-001-004 and 001-004                          |
            -- | 12/05/16 |  ---   | B Hernandez |         | Port to PostgreSQL                                       |
            -- | 17/06/19 |  ---   | M Walsh     |         | Python3 Migration                                        |
            -----------------------------------------------------------------------------------------------------------
            --                                     Integrity Test Steps                                              --
            -----------------------------------------------------------------------------------------------------------
            -- 001  nominal_ledger_balance_check                                                                     --
            -- 002  nominal_ledger_rounding_check                                                                    --
            -- 003  transaction_sequence_number_unique                                                               --
            -- 004  purchase_calculation                                                                             --
            -- 005  balance_calculation                                                                              --
            -- 006  sanity_check                                                                                     --
            -----------------------------------------------------------------------------------------------------------
            -- Global variables for each step                                                                        --
            -- Each step should re-initialise these variables if used                                                --
            -----------------------------------------------------------------------------------------------------------
            DECLARE
                total_records_inspected integer;
                total_defects_found integer;
                time_started timestamp without time zone;
                time_finished timestamp without time zone;
                records_inspected integer;
                defects_found integer;
                skip_credits integer[];
                transaction_date timestamp without time zone;
                credits decimal(23, 4);
                debits decimal(23,4);
                balance decimal(23, 4);
                r record;

            BEGIN
            time_started := clock_timestamp();
            total_records_inspected := 0;
            total_defects_found := 0;
            skip_credits := ARRAY[32409];

            RAISE NOTICE '============================================================================================';
            RAISE NOTICE 'Test Start DateTime %s', CAST(time_started AS varchar);
            RAISE NOTICE '============================================================================================';
            -----------------------------------------------------------------------------------------------------------
            --                   001  nominal_ledger_balance_check
            -----------------------------------------------------------------------------------------------------------
            -- Evaluates for every nominal_ledger_id if there are records where the debits and credits don't ,       --
            -- balance, and saves the nominal_ledger_id of these ones in a temporary table, then send by email       --
            -- the encountered wrong records.                                                                        --
            -----------------------------------------------------------------------------------------------------------
            records_inspected := 0;
            defects_found := 0;

            RAISE NOTICE '============================================================================================';
            RAISE NOTICE '--- 001 nominal_ledger_balance_check ---';

            SELECT SUM(total) INTO records_inspected
            FROM (SELECT COUNT(id) AS total
                FROM nominal_ledger
                WHERE deleted IS NULL
                UNION ALL
                SELECT COUNT(nominal_ledger_id) AS total
                FROM nominal_ledger_debits
                WHERE deleted IS NULL
                UNION ALL
                SELECT COUNT(nominal_ledger_id) AS total
                FROM nominal_ledger_credits
                WHERE deleted IS NULL) t;

            DROP TABLE IF EXISTS failed_journals;
            CREATE TEMPORARY TABLE failed_journals (nominal_ledger_id int);

            FOR r IN SELECT id
                FROM nominal_ledger
                WHERE deleted IS  NULL

            LOOP
                SELECT SUM(nominal_ledger_debits.amount) INTO debits
                FROM nominal_ledger_debits
                WHERE nominal_ledger_id = r.id AND deleted IS NULL;
                SELECT SUM(nominal_ledger_credits.amount) INTO credits
                FROM nominal_ledger_credits
                WHERE nominal_ledger_id = r.id AND deleted IS NULL;
                IF debits != credits THEN
                    defects_found := defects_found + 1;
                    RAISE NOTICE 'Nominal Ledger Balance Calculation Error nominal_ledger_id %', CAST(r.id as VARCHAR);
                    INSERT INTO failed_journals (nominal_ledger_id)
                    values (r.id);
                END IF;
            END LOOP;

            SELECT COUNT(nominal_ledger_id) INTO defects_found
            FROM failed_journals;

            total_records_inspected := total_records_inspected + records_inspected;
            total_defects_found := total_defects_found + defects_found;

            drop table failed_journals;

            RAISE NOTICE '% records inspected', CAST(records_inspected as varchar);
            RAISE NOTICE '% defects found', CAST(defects_found as varchar);

            -----------------------------------------------------------------------------------------------------------
            --               002  nominal_ledger_rounding_check                                                      --
            -----------------------------------------------------------------------------------------------------------
            -- Evaluates for every Credit and Debit if there are records where the unit_price * quantity don't match --
            -- the credit amounts or debit amounts. If unit_price or quantity is 0 the row will be skipped.          --
            -- Errors will be entered in a temporary table and send by email.                                        --
            -----------------------------------------------------------------------------------------------------------
            records_inspected := 0;
            defects_found := 0;

            RAISE NOTICE '============================================================================================';
            RAISE NOTICE '--- 002  nominal_ledger_rounding_check ---';

            -- Create a table to keep the wrong idCredits and idDebits
            DROP TABLE IF EXISTS failed_rounding;
            CREATE TEMPORARY TABLE failed_rounding (id int, credit_or_debit char(1));

            SELECT SUM(total) INTO records_inspected
            FROM (SELECT COUNT(id) AS total
                FROM nominal_ledger
                WHERE deleted IS NULL
                UNION ALL
                SELECT COUNT(nominal_ledger_id) AS total
                FROM nominal_ledger_debits
                WHERE deleted IS NULL
                UNION ALL
                SELECT COUNT(nominal_ledger_id) AS total
                FROM nominal_ledger_credits
                WHERE deleted IS NULL) t;

            SELECT SUM(failed) INTO defects_found
            FROM (SELECT COUNT(id) AS failed
                FROM nominal_ledger_debits
                WHERE quantity != 0  AND unit_price != 0
                    AND ROUND(unit_price * quantity, 2) != nominal_ledger_debits.amount AND deleted IS NULL
                UNION ALL
                SELECT COUNT(id) AS failed
                FROM nominal_ledger_credits
                WHERE id NOT IN (
                    SELECT unnest(skip_credits)) AND quantity != 0  AND unit_price != 0
                        AND ROUND(unit_price * quantity, 2) != nominal_ledger_credits.amount AND deleted IS NULL) t;

            IF defects_found > 0 THEN
                -- insert wrong ids into the table
                INSERT INTO failed_rounding (id, credit_or_debit)
                SELECT id, 'd'
                FROM nominal_ledger_debits
                WHERE quantity != 0 AND unit_price != 0
                    AND ROUND(unit_price * quantity, 2) != nominal_ledger_debits.amount;

                INSERT INTO failed_rounding (id, credit_or_debit)
                SELECT id, 'c'
                FROM nominal_ledger_credits
                WHERE id NOT IN (
                    SELECT unnest(skip_credits)) AND quantity != 0  AND unit_price != 0
                        AND ROUND(unit_price * quantity, 2) != nominal_ledger_credits.amount;

                FOR r IN SELECT *
                     FROM failed_rounding
                LOOP
                    RAISE NOTICE 'Rounding issue in % %', CAST(r.id AS varchar), CAST(r.credit_or_debit AS varchar);
                END LOOP;
            END IF;

            total_records_inspected := total_records_inspected + records_inspected;
            total_defects_found := total_defects_found + defects_found;

            DROP TABLE failed_rounding;

            RAISE NOTICE '% records inspected', CAST(records_inspected as varchar);
            RAISE NOTICE '% defects found', CAST(defects_found as varchar);

            -----------------------------------------------------------------------------------------------------------
            --                         003  transaction_sequence_number_unique                                       --
            -----------------------------------------------------------------------------------------------------------
            -- For an address_id there are no repeated transaction_sequence_number for the same transaction_type_id. --
            -- Example:                                                                                              --
            --      address_id   tsn    transaction_type_id                                                          --
            --      1            1      10001                                                                        --
            --      1            1      10001 (Duplicated, invalid)                                                  --
            --      2            1      10002 (Valid)                                                                --
            -----------------------------------------------------------------------------------------------------------
            records_inspected := 0;
            defects_found := 0;
            RAISE NOTICE '============================================================================================';
            RAISE NOTICE '--- 003 transaction_sequence_number_unique ---';

            FOR r IN SELECT "address_id", "transaction_type_id", "transaction_sequence_number"
                FROM nominal_ledger
                WHERE deleted IS  NULL
            LOOP
                IF (SELECT COUNT(*)
                    FROM nominal_ledger
                    WHERE ("address_id" = r."address_id") AND ("transaction_type_id" = r."transaction_type_id")
                        AND ("transaction_sequence_number" = r."transaction_sequence_number")
                        AND (deleted IS NULL)) > 1 THEN
                    defects_found := defects_found + 1;
                    RAISE NOTICE 'transaction_sequence_number NOT Unique';
                    RAISE NOTICE 'address_id %', CAST(r."address_id" as varchar);
                    RAISE NOTICE 'transaction_type_id %', CAST(r."transaction_type_id" as varchar);
                    RAISE NOTICE 'transaction_sequence_number %', CAST(r."transaction_sequence_number" as varchar);
                END IF;
            END LOOP;

            total_records_inspected := total_records_inspected + records_inspected;
            total_defects_found := total_defects_found + defects_found;

            RAISE NOTICE '% records inspected', CAST(records_inspected as varchar);
            RAISE NOTICE '% defects found', CAST(defects_found as varchar);

            -----------------------------------------------------------------------------------------------------------
            --                                      004  purchase_calculation                                        --
            -----------------------------------------------------------------------------------------------------------
            -- Credits and Debits calculated to see if balance. There is -+ 2p on a purchase transaction.            --
            -----------------------------------------------------------------------------------------------------------
            records_inspected := 0;
            defects_found := 0;

            RAISE NOTICE '============================================================================================';
            RAISE NOTICE  '--- 004 purchase_calculation ---';

            DROP TABLE IF EXISTS failed_journal;
            CREATE TEMPORARY TABLE failed_journal (nominal_ledger_id int);

            SELECT COUNT(id) INTO records_inspected
            FROM nominal_ledger
            WHERE deleted IS NULL;

            FOR r in SELECT id
                FROM nominal_ledger
                WHERE deleted is NULL

            LOOP
                SELECT SUM(nominal_ledger_debits.amount) INTO debits
                FROM nominal_ledger_debits
                WHERE nominal_ledger_id = r.id AND deleted IS NULL AND nominal_account_number != 2210
                    AND nominal_ledger_debits.amount IS NOT NULL;
                SELECT SUM(nominal_ledger_credits.amount) INTO credits
                FROM nominal_ledger_credits
                WHERE nominal_ledger_id = r.id AND deleted IS NULL
                    AND nominal_account_number != 2210 and nominal_ledger_credits.amount IS NOT NULL;
                IF (debits != credits) OR credits IS NULL or debits IS NULL THEN
                    SELECT ROUND(SUM((quantity * unit_price) * (tax_rate / 100) + quantity * unit_price), 2) INTO debits
                    FROM nominal_ledger_debits
                    WHERE nominal_ledger_id = r.id AND deleted IS NULL AND nominal_account_number != 2210
                        AND quantity IS NOT NULL AND unit_price IS NOT NULL AND tax_rate IS NOT NULL;
                    SELECT SUM(nominal_ledger_credits.amount) INTO credits
                    FROM nominal_ledger_credits
                    WHERE nominal_ledger_id = r.id AND deleted IS NULL AND nominal_account_number != 2210
                        AND tax_rate IS NOT NULL;
                    IF debits != credits AND debits - credits > 0.02 AND credits - debits > 0.02 THEN
                        SELECT SUM(nominal_ledger_debits.amount) into debits
                        FROM nominal_ledger_debits
                        WHERE nominal_ledger_id = r.id AND deleted IS NULL AND nominal_account_number != 2210
                            AND tax_rate IS NOT NULL;
                        SELECT ROUND(
                            SUM((quantity * unit_price) * (tax_rate / 100) + quantity * unit_price), 2) INTO credits
                        FROM nominal_ledger_credits
                        WHERE nominal_ledger_id = r.id AND deleted IS NULL AND nominal_account_number != 2210
                            AND quantity IS NOT NULL AND unit_price IS NOT NULL AND tax_rate IS NOT NULL;
                        IF debits != credits AND debits - credits > 0.02 AND credits - debits > 0.02 THEN
                            RAISE NOTICE 'Balance Calculation Error nominal_ledger_id %', CAST(r.id as VARCHAR);
                            INSERT INTO failed_journal (nominal_ledger_id)
                            values (r.id);
                        END IF;
                    END IF;
                END IF;
            END LOOP;

            SELECT COUNT(*) INTO defects_found
            FROM failed_journal;

            total_records_inspected := total_records_inspected + records_inspected;
            total_defects_found := total_defects_found + defects_found;

            RAISE NOTICE '% records inspected', CAST(records_inspected as varchar);
            RAISE NOTICE '% defects found', CAST(defects_found as varchar);

            -----------------------------------------------------------------------------------------------------------
            --                                      005  balance_calculation                                         --
            -----------------------------------------------------------------------------------------------------------
            -- Check if nominal_ledger_credits and nominal_ledger_debits balance. The procedure calculates the       --
            -- balance and checks it. Exact check is done on 11002 Account Sale Invoice.                             --
            -- Check is done from Start of 2013 because of error before that date.                                   --
            -----------------------------------------------------------------------------------------------------------
            records_inspected := 0;
            defects_found := 0;

            RAISE NOTICE '============================================================================================';
            RAISE NOTICE '--- 005 balance_calculation ----';

            DROP TABLE IF EXISTS error_journal;
            CREATE TEMPORARY TABLE error_journal (nominal_ledger_id int);

            SELECT COUNT(id) INTO records_inspected
            FROM nominal_ledger
            WHERE deleted IS NULL;

            FOR r IN SELECT id, unallocated_balance, transaction_sequence_number, transaction_date
                     FROM nominal_ledger
                     WHERE transaction_type_id = 11002 AND transaction_date > '2013/01/01' AND deleted IS NULL
            LOOP
                SELECT SUM(nominal_ledger_debits.amount) INTO debits
                FROM nominal_ledger_debits
                WHERE nominal_ledger_id = r.id AND deleted IS NULL AND nominal_account_number != 2210
                    AND nominal_ledger_debits.amount IS NOT NULL;
                SELECT SUM(nominal_ledger_credits.amount) INTO credits
                FROM nominal_ledger_credits
                WHERE nominal_ledger_id = r.id AND deleted IS NULL
                    AND nominal_account_number != 2210 AND nominal_ledger_credits.amount IS NOT NULL;
                IF debits != credits OR credits IS NULL OR debits IS NULL THEN
                    SELECT SUM((quantity * unit_price) * (tax_rate / 100) + quantity * unit_price) INTO debits
                    FROM nominal_ledger_debits
                    WHERE nominal_ledger_id = r.id AND deleted IS NULL AND nominal_account_number != 2210
                         AND quantity IS NOT NULL AND unit_price IS NOT NULL AND tax_rate IS NOT NULL;
                    SELECT ROUND(debits, 4) into debits;
                    SELECT SUM(nominal_ledger_credits.amount) INTO credits
                    FROM nominal_ledger_credits
                    WHERE nominal_ledger_id = r.id AND deleted IS NULL AND nominal_account_number != 2210
                        AND tax_rate IS NOT NULL;
                    IF debits != credits OR debits IS NULL OR credits IS NULL THEN
                        SELECT SUM(nominal_ledger_debits.amount) INTO debits
                        FROM nominal_ledger_debits
                        WHERE nominal_ledger_id = r.id AND deleted IS NULL AND nominal_account_number != 2210
                            AND tax_rate IS NOT NULL;
                        SELECT SUM((quantity * unit_price) * (tax_rate / 100) + quantity * unit_price) INTO credits
                        FROM nominal_ledger_credits
                        WHERE nominal_ledger_id = r.id AND deleted IS NULL AND nominal_account_number != 2210
                            AND quantity IS NOT NULL AND unit_price IS NOT NULL AND tax_rate IS NOT NULL;
                        SELECT ROUND(credits, 4) INTO credits;
                        IF debits != credits OR debits IS NULL OR credits IS NULL THEN
                            SELECT ROUND(debits, 2) into debits;
                            SELECT ROUND(credits, 2) INTO credits;
                            IF debits != credits OR debits IS NULL OR credits IS NULL THEN
                                RAISE NOTICE 'Balance Calculation Error';
                                RAISE NOTICE 'nominal_ledger_id %', CAST(r.id as VARCHAR);
                                RAISE NOTICE 'unallocated_balance %', CAST(r.unallocated_balance as VARCHAR);
                                RAISE NOTICE 'tsn %', CAST(r.transaction_sequence_number as VARCHAR);
                                RAISE NOTICE 'transaction_date %', CAST(r."transaction_date" as VARCHAR);
                                INSERT INTO error_journal (nominal_ledger_id)
                                values (r.id);
                            END IF;
                        END IF;
                    END IF;
                END IF;
            END LOOP;

            SELECT COUNT(*) INTO defects_found
            FROM error_journal;

            total_records_inspected := total_records_inspected + records_inspected;
            total_defects_found := total_defects_found + defects_found;

            RAISE NOTICE '% records inspected', CAST(records_inspected as varchar);
            RAISE NOTICE '% defects found', CAST(defects_found as varchar);

            -----------------------------------------------------------------------------------------------------------
            --                                           006  sanity_check                                           --
            -----------------------------------------------------------------------------------------------------------
            -- Check if nominal_ledger_credits and nominal_ledger_debits balance.
            -- The procedure calculates the balance and checks it. Exact check is done on 11002 Account Sale Invoice.
            -- Check is done from Start of 2013 because of error before that date.
            -----------------------------------------------------------------------------------------------------------
            records_inspected := 0;
            defects_found := 0;

            RAISE NOTICE '============================================================================================';
            RAISE NOTICE '--- 006 sanity_check ---';

            DROP TABLE IF EXISTS period_ends_table;
            DROP TABLE IF EXISTS bad_period_end;
            CREATE TEMPORARY TABLE period_ends_table (
                nominal_ledger_id int,
                address_id int,
                tdate timestamp without time zone,
                period_balance decimal(23, 4));
            CREATE TEMPORARY TABLE bad_period_end (nominal_ledger_id int, dif decimal(23,4));

            INSERT INTO period_ends_table
            (nominal_ledger_id, address_id, tdate, period_balance)
            SELECT id, "address_id", "transaction_date", period_end_balance
            FROM nominal_ledger
            WHERE "transaction_type_id" = 12001 AND deleted IS NULL AND period_end_balance IS NOT NULL;

            FOR r IN SELECT nominal_ledger_id, address_id, tdate, period_balance
                FROM period_ends_table
            LOOP
                records_inspected := records_inspected + 1;
                SELECT transaction_date INTO transaction_date
                FROM nominal_ledger
                WHERE transaction_type_id = 12001 and deleted IS NULL AND period_end_balance IS NOT NULL
                    AND transaction_date < r.tdate
                ORDER BY transaction_date DESC LIMIT 1;

                IF  transaction_date IS NULL THEN
                    transaction_date := '1753-01-01';
                END IF;

                SELECT COALESCE(SUM(COALESCE(nominal_ledger_debits.amount, 0)), 0) INTO debits
                FROM nominal_ledger nominal_ledger
                INNER JOIN nominal_ledger_debits
                ON nominal_ledger.id = nominal_ledger_debits.nominal_ledger_id
                WHERE nominal_ledger.deleted IS NULL and nominal_ledger_debits.deleted IS NULL
                    AND nominal_ledger.address_id = r.address_id
                    AND nominal_ledger.transaction_date BETWEEN transaction_date and r.tdate
                    AND ((nominal_ledger.transaction_type_id BETWEEN 10000 AND 10005) OR
                        (nominal_ledger.transaction_type_id BETWEEN 11000 and 11005));
                SELECT COALESCE(SUM(COALESCE(nominal_ledger_credits.amount, 0)), 0) INTO credits
                FROM nominal_ledger nominal_ledger
                INNER JOIN nominal_ledger_credits
                ON nominal_ledger.id = nominal_ledger_credits.nominal_ledger_id
                WHERE nominal_ledger.deleted IS NULL AND nominal_ledger_credits.deleted IS NULL
                    AND nominal_ledger.address_id = r.address_id
                    AND nominal_ledger.transaction_date BETWEEN transaction_date and r.tdate
                    AND ((nominal_ledger.transaction_type_id BETWEEN 10000 and 10005) OR
                        (nominal_ledger.transaction_type_id BETWEEN 11000 and 11005));

                RAISE NOTICE 'nominal_ledger_id: %', CAST (r.nominal_ledger_id as varchar);
                RAISE NOTICE 'Debits: %', CAST (debits as varchar);
                RAISE NOTICE 'Credits: %', CAST (credits as varchar);
                RAISE NOTICE 'Actual Balance: %', CAST ((credits - debits) as varchar(30));
                RAISE NOTICE 'Balance: %', CAST (r.period_balance as varchar);
                RAISE NOTICE '----------------------------------------------------------------------------------------';
                If credits - debits = 0 THEN
                    IF debits != r.period_balance THEN
                        INSERT INTO bad_period_end (nominal_ledger_id, dif)
                        VALUES (r.nominal_ledger_id, (debits - r.period_balance));
                        RAISE NOTICE '--- 006 sanity_check nominal_ledger_id --- %',
                        CAST(r.nominal_ledger_id as varchar);
                    END IF;
                ELSE
                    INSERT INTO bad_period_end (nominal_ledger_id, dif)
                    Values (r.nominal_ledger_id, (credits - debits));
                    RAISE NOTICE '--- 006 sanity_check nominal_ledger_id --- %', CAST(r.nominal_ledger_id as varchar);
                END IF;
            END LOOP;

            SELECT COUNT(*) INTO defects_found
            FROM bad_period_end;

            DROP TABLE period_ends_table;
            DROP TABLE bad_period_end;

            RAISE NOTICE '% records inspected', CAST(records_inspected as varchar);
            RAISE NOTICE '% defects found', CAST(defects_found as varchar);

            total_records_inspected := total_records_inspected + records_inspected;
            total_defects_found := total_defects_found + defects_found;

            RAISE NOTICE '============================================================================================';
            RAISE NOTICE 'Total Records inspected %', cast (total_records_inspected as varchar);
            RAISE NOTICE 'Total Defects Found %', cast(total_defects_found as varchar);

            time_finished := clock_timestamp();
            RAISE NOTICE '============================================================================================';
            RAISE NOTICE 'Test Finish DateTime %', CAST(time_finished AS varchar);
            RAISE NOTICE '============================================================================================';

            -----------------------------------------------------------------------------------------------------------
            --  Save final results for this run into the results table                                               --
            -----------------------------------------------------------------------------------------------------------
            INSERT INTO "IntegrityTest"
                ("start_time", "finish_time", "records_tested", "errors_found")
            Values
                (time_started , time_finished, total_records_inspected, total_defects_found);

            -----------------------------------------------------------------------------------------------------------
            -- Truncate Integrity Test table.
            -----------------------------------------------------------------------------------------------------------
            DELETE FROM "IntegrityTest"
            WHERE "start_time" < now() at time zone 'UTC' - interval '2 year';

            RETURN total_defects_found;
            END
            $BODY$
            LANGUAGE plpgsql VOLATILE
              COST 100;
        """),
    ]
