# Generated by Django 5.1.6 on 2025-04-01 16:33

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trading', '0017_alter_wallet_balance'),
    ]

    operations = [
        migrations.AlterField(
            model_name='trade',
            name='timestamp',
            field=models.DateTimeField(default=datetime.datetime(2025, 4, 1, 16, 33, 23, 906732, tzinfo=datetime.timezone.utc)),
        ),
    ]
