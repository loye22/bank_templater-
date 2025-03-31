from django.db import models
import uuid  

class Statement(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)  # UUID as primary key
    statement_number = models.IntegerField(unique=True)
    period = models.TextField()
    initial_balance = models.DecimalField(max_digits=15, decimal_places=2)
    final_balance = models.DecimalField(max_digits=15, decimal_places=2)
    first_date = models.DateField()
    last_date = models.DateField()

    def __str__(self):
        return f"Statement {self.statement_number} ({self.first_date} - {self.last_date})"

    class Meta:
        ordering = ['statement_number']

class DailySummary(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)  # UUID as primary key
    statement = models.ForeignKey(Statement, on_delete=models.CASCADE, related_name='daily_summaries')
    date = models.DateField()
    debit = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    credit = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    daily_final_balance = models.DecimalField(max_digits=15, decimal_places=2)
    transaction_count = models.IntegerField(default=0)
    balance_verified = models.BooleanField(default=True)

    def __str__(self):
        return f"Summary for {self.date} (Statement {self.statement.statement_number})"

    class Meta:
        ordering = ['date']
        unique_together = ('statement', 'date')

class Transaction(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)  # UUID as primary key
    daily_summary = models.ForeignKey(DailySummary, on_delete=models.CASCADE, related_name='transactions')
    debit = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    credit = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    value = models.DecimalField(max_digits=15, decimal_places=2)
    value_type = models.CharField(max_length=6, choices=[('Debit', 'Debit'), ('Credit', 'Credit')])
    date = models.DateField()
    description = models.TextField()
    iban_partner = models.CharField(max_length=34, blank=True, null=True)
    initial_sold = models.DecimalField(max_digits=15, decimal_places=2)
    final_sold = models.DecimalField(max_digits=15, decimal_places=2)
    partner_name = models.CharField(max_length=100, blank=True, null=True)
    transaction_type = models.CharField(max_length=50, blank=True, null=True)
    reference = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"Transaction on {self.date}: {self.value} {self.value_type}"

    class Meta:
        ordering = ['date', 'id']