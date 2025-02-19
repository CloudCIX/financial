# Generated by Django 2.2 on 2024-10-15 17:08

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('financial', '0006_unit_price_precision'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            ALTER TABLE statement_settings
            ALTER COLUMN day
            TYPE jsonb
            USING jsonb_build_array(day);
            """,
            reverse_sql="""
            ALTER TABLE statement_settings
            ALTER COLUMN day
            TYPE integer
            USING (day->>0)::integer;
            """,
        ),
        migrations.AlterField(
            model_name='statementsettings',
            name='day',
            field=django.contrib.postgres.fields.jsonb.JSONField(default=list),
        ),
        migrations.AlterModelOptions(
            name='addressnominalaccount',
            options={'ordering': ['-address_id']},
        ),
        migrations.AlterModelOptions(
            name='globalnominalaccount',
            options={'ordering': ['description']},
        ),
        migrations.AlterModelOptions(
            name='nominalaccounttype',
            options={'ordering': ['description']},
        ),
        migrations.AlterModelOptions(
            name='nominalcontra',
            options={'ordering': ['global_nominal_account_id']},
        ),
        migrations.AlterModelOptions(
            name='nominalledger',
            options={'ordering': ['transaction_date']},
        ),
        migrations.AlterModelOptions(
            name='paymentmethod',
            options={'ordering': ['description']},
        ),
        migrations.AlterModelOptions(
            name='taxrate',
            options={'ordering': ['address_id']},
        ),
        migrations.AddIndex(
            model_name='addressnominalaccount',
            index=models.Index(fields=['deleted'], name='address_account_deleted'),
        ),
        migrations.AddIndex(
            model_name='allocation',
            index=models.Index(fields=['created'], name='allocation_created'),
        ),
        migrations.AddIndex(
            model_name='allocation',
            index=models.Index(fields=['deleted'], name='allocation_deleted'),
        ),
        migrations.AddIndex(
            model_name='globalnominalaccount',
            index=models.Index(fields=['deleted'], name='global_account_deleted'),
        ),
        migrations.AddIndex(
            model_name='nominalaccounttype',
            index=models.Index(fields=['deleted'], name='account_type_deleted'),
        ),
        migrations.AddIndex(
            model_name='nominalcontra',
            index=models.Index(fields=['deleted'], name='nom_contra_deleted'),
        ),
        migrations.AddIndex(
            model_name='nominalledger',
            index=models.Index(fields=['id'], name='ledger_id'),
        ),
        migrations.AddIndex(
            model_name='nominalledger',
            index=models.Index(fields=['deleted'], name='ledger_deleted'),
        ),
        migrations.AddIndex(
            model_name='nominalledgercredit',
            index=models.Index(fields=['id'], name='ledger_credit_id'),
        ),
        migrations.AddIndex(
            model_name='nominalledgercredit',
            index=models.Index(fields=['deleted'], name='ledger_credit_deleted'),
        ),
        migrations.AddIndex(
            model_name='nominalledgerdebit',
            index=models.Index(fields=['id'], name='ledger_debit_id'),
        ),
        migrations.AddIndex(
            model_name='nominalledgerdebit',
            index=models.Index(fields=['deleted'], name='ledger_debit_deleted'),
        ),
        migrations.AddIndex(
            model_name='paymentmethod',
            index=models.Index(fields=['deleted'], name='payment_method_deleted'),
        ),
        migrations.AddIndex(
            model_name='statementsettings',
            index=models.Index(fields=['address_id'], name='statement_settings_address_id'),
        ),
        migrations.AddIndex(
            model_name='statementsettings',
            index=models.Index(fields=['day'], name='statement_settings_day'),
        ),
        migrations.AddIndex(
            model_name='statementsettings',
            index=models.Index(fields=['min_credit'], name='statement_settings_min_credit'),
        ),
        migrations.AddIndex(
            model_name='statementsettings',
            index=models.Index(fields=['min_debit'], name='statement_settings_min_debit'),
        ),
        migrations.AddIndex(
            model_name='taxrate',
            index=models.Index(fields=['address_id'], name='tax_rate_address_id'),
        ),
        migrations.AddIndex(
            model_name='taxrate',
            index=models.Index(fields=['deleted'], name='tax_rate_deleted'),
        ),
    ]
