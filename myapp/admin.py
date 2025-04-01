from django.contrib import admin
from .models import Statement, DailySummary, Transaction , ProcessedFile
class TransactionInline(admin.TabularInline):
    model = Transaction
    extra = 0
    fields = ['id' , 'date', 'value', 'value_type', 'partner_name', 'transaction_type', 'description', 'reference' , 'initial_sold', 'final_sold']
    readonly_fields= ['id']  

class DailySummaryInline(admin.TabularInline):
    model = DailySummary
    extra = 0
    fields = ['id' , 'date', 'debit', 'credit', 'daily_final_balance', 'transaction_count', 'balance_verified']
    readonly_fields= ['id'] 
    inlines = [TransactionInline]

@admin.register(Statement)
class StatementAdmin(admin.ModelAdmin):
    list_display = ['id' , 'statement_number', 'period', 'initial_balance', 'final_balance', 'first_date', 'last_date']
    list_filter = ['first_date', 'last_date']
    search_fields = ['statement_number', 'period']
    inlines = [DailySummaryInline]
    

@admin.register(DailySummary)
class DailySummaryAdmin(admin.ModelAdmin):
    list_display = ['id' , 'date', 'statement', 'debit', 'credit', 'daily_final_balance', 'transaction_count', 'balance_verified']
    list_filter = ['date', 'balance_verified']
    search_fields = ['statement__statement_number']
    inlines = [TransactionInline]

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['id' , 'date', 'value', 'value_type', 'partner_name', 'transaction_type', 'reference', 'daily_summary']
    list_filter = ['date', 'value_type', 'transaction_type']
    search_fields = ['description', 'partner_name', 'reference', 'iban_partner']


@admin.register(ProcessedFile)
class ProcessedFileAdmin(admin.ModelAdmin):
    list_display = ('file', 'processed_at', 'description')
