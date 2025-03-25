# Generated by Django 5.1.6 on 2025-03-24 13:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trading', '0003_stock_volume'),
    ]

    operations = [
        migrations.AddField(
            model_name='stock',
            name='high_52',
            field=models.IntegerField(default=500),
        ),
        migrations.AddField(
            model_name='stock',
            name='low_52',
            field=models.IntegerField(default=200),
        ),
        migrations.AddField(
            model_name='stock',
            name='market_cap',
            field=models.IntegerField(default=500),
        ),
    ]
