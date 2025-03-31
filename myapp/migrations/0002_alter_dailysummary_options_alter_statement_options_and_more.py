# Generated by Django 5.1.7 on 2025-03-31 07:52

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='dailysummary',
            options={'ordering': ['date']},
        ),
        migrations.AlterModelOptions(
            name='statement',
            options={'ordering': ['statement_number']},
        ),
        migrations.AlterModelOptions(
            name='transaction',
            options={'ordering': ['date', 'id']},
        ),
        migrations.AddField(
            model_name='dailysummary',
            name='balance_verified',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='transaction',
            name='partner_name',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='transaction',
            name='reference',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='transaction',
            name='transaction_type',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='dailysummary',
            name='statement',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='daily_summaries', to='myapp.statement'),
        ),
        migrations.AlterField(
            model_name='statement',
            name='statement_number',
            field=models.IntegerField(unique=True),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='daily_summary',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transactions', to='myapp.dailysummary'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='value_type',
            field=models.CharField(choices=[('Debit', 'Debit'), ('Credit', 'Credit')], max_length=6),
        ),
        migrations.AlterUniqueTogether(
            name='dailysummary',
            unique_together={('statement', 'date')},
        ),
    ]
