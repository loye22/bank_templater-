# Generated by Django 5.1.7 on 2025-03-31 08:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0002_alter_dailysummary_options_alter_statement_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dailysummary',
            name='credit',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=15),
        ),
        migrations.AlterField(
            model_name='dailysummary',
            name='debit',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=15),
        ),
        migrations.AlterField(
            model_name='dailysummary',
            name='transaction_count',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='credit',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=15),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='debit',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=15),
        ),
    ]
