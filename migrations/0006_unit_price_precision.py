# Generated by Django 2.2.11 on 2020-05-13 08:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('financial', '0005_optional_contra_address_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='nominalledgercredit',
            name='unit_price',
            field=models.DecimalField(decimal_places=8, max_digits=23, null=True),
        ),
        migrations.AlterField(
            model_name='nominalledgerdebit',
            name='unit_price',
            field=models.DecimalField(decimal_places=8, max_digits=23, null=True),
        ),
    ]
