# Generated by Django 2.2.10 on 2020-03-02 11:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('financial', '0003_integrity'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='nominalledger',
            index=models.Index(fields=['address_id'], name='ledger_address_id'),
        ),
    ]
