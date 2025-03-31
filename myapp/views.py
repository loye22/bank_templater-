# import logging
# from django.shortcuts import render
# from django.http import HttpResponse
# from django.db import transaction
# import json
# from .models import Statement, DailySummary, Transaction

# # Set up logging
# logger = logging.getLogger(__name__)

# def import_json(request):
#     if request.method == 'POST':
#         try:
#             # Check if the file is provided
#             if 'json_file' not in request.FILES:
#                 return HttpResponse("Error: No JSON file uploaded.", status=400)

#             json_file = request.FILES['json_file']
#             data = json.load(json_file)

#             # Log the entire JSON data for debugging
#             logger.info("Imported JSON data: %s", json.dumps(data, indent=2))

#             # Validate top-level structure
#             if 'statements' not in data:
#                 return HttpResponse("Error: JSON must contain a 'statements' key.", status=400)

#             if not isinstance(data['statements'], list):
#                 return HttpResponse("Error: 'statements' must be a list.", status=400)

#             with transaction.atomic():
#                 for idx, stmt_data in enumerate(data['statements'], 1):
#                     # Validate required fields for Statement
#                     required_fields = ['StatementNumber', 'StatementNumberPeriod', 'InitialBalanceValue', 
#                                      'FinalBalanceValue', 'First Date', 'Last Date']
#                     missing_fields = [field for field in required_fields if field not in stmt_data]
#                     if missing_fields:
#                         # Log the statement data for debugging
#                         logger.error("Statement %d data: %s", idx, json.dumps(stmt_data, indent=2))
#                         return HttpResponse(f"Error: Missing fields in statement {idx}: {missing_fields}", status=400)

#                     statement, _ = Statement.objects.update_or_create(
#                         statement_number=stmt_data['StatementNumber'],
#                         defaults={
#                             'period': stmt_data['StatementNumberPeriod'],
#                             'initial_balance': stmt_data['InitialBalanceValue'],
#                             'final_balance': stmt_data['FinalBalanceValue'],
#                             'first_date': stmt_data['First Date'],
#                             'last_date': stmt_data['Last Date'],
#                         }
#                     )

#                     # Validate and process Daily Summaries
#                     if 'DailySummaries' not in stmt_data:
#                         return HttpResponse(f"Error: Statement {idx} missing 'DailySummaries'.", status=400)

#                     for daily_idx, daily_data in enumerate(stmt_data['DailySummaries'], 1):
#                         daily_required_fields = ['Date', 'Debit', 'Credit', 'DailyFinalBalanceValue', 
#                                                'Transaction Counts', 'DailyBalanceVerificiation']
#                         daily_missing = [field for field in daily_required_fields if field not in daily_data]
#                         if daily_missing:
#                             return HttpResponse(f"Error: Missing fields in DailySummary {daily_idx} of Statement {idx}: {daily_missing}", status=400)

#                         daily_summary, _ = DailySummary.objects.update_or_create(
#                             statement=statement,
#                             date=daily_data['Date'],
#                             defaults={
#                                 'debit': daily_data['Debit'],
#                                 'credit': daily_data['Credit'],
#                                 'daily_final_balance': daily_data['DailyFinalBalanceValue'],
#                                 'transaction_count': daily_data['Transaction Counts'],
#                                 'balance_verified': daily_data['DailyBalanceVerificiation'],
#                             }
#                         )

#                         # Validate and process Transactions
#                         if 'Transactions' not in daily_data:
#                             return HttpResponse(f"Error: DailySummary {daily_idx} in Statement {idx} missing 'Transactions'.", status=400)

#                         for trans_idx, trans_data in enumerate(daily_data['Transactions'], 1):
#                             trans_required_fields = ['Debit', 'Credit', 'Value', 'ValueType', 'Date', 
#                                                    'Table Body', 'IBAN Partner', 'InitialSold', 'FinalSold']
#                             trans_missing = [field for field in trans_required_fields if field not in trans_data]
#                             if trans_missing:
#                                 return HttpResponse(f"Error: Missing fields in Transaction {trans_idx} of DailySummary {daily_idx} in Statement {idx}: {trans_missing}", status=400)

#                             Transaction.objects.update_or_create(
#                                 daily_summary=daily_summary,
#                                 date=trans_data['Date'],
#                                 value=trans_data['Value'],
#                                 value_type=trans_data['ValueType'],
#                                 defaults={
#                                     'debit': trans_data['Debit'],
#                                     'credit': trans_data['Credit'],
#                                     'description': trans_data['Table Body'],
#                                     'iban_partner': trans_data['IBAN Partner'] or None,
#                                     'initial_sold': trans_data['InitialSold'],
#                                     'final_sold': trans_data['FinalSold'],
#                                     'partner_name': trans_data.get('Partner Name'),
#                                     'transaction_type': trans_data.get('Transaction Type'),
#                                     'reference': trans_data.get('Table Body', '').split('REF: ')[-1].split()[0] if 'REF: ' in trans_data.get('Table Body', '') else None,
#                                 }
#                             )

#             return HttpResponse("Import successful!", status=200)

#         except json.JSONDecodeError as e:
#             logger.error("JSON decode error: %s", str(e))
#             return HttpResponse(f"Error: Invalid JSON format: {str(e)}", status=400)
#         except Exception as e:
#             logger.error("Unexpected error during import: %s", str(e))
#             return HttpResponse(f"Error during import: {str(e)}", status=400)

#     return render(request, 'import.html')




import logging
import json
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.db import transaction
from .models import Statement, DailySummary, Transaction

logger = logging.getLogger(__name__)

def import_json(request):
    if request.method == 'POST':
        try:
            if 'json_file' not in request.FILES:
                return HttpResponse("Error: No JSON file uploaded.", status=400)

            json_file = request.FILES['json_file']
            data = json.load(json_file)

            logger.info("Imported JSON data: %s", json.dumps(data, indent=2))

            if 'statements' not in data:
                return HttpResponse("Error: JSON must contain a 'statements' key.", status=400)

            if not isinstance(data['statements'], list):
                return HttpResponse("Error: 'statements' must be a list.", status=400)

            with transaction.atomic():
                for idx, stmt_data in enumerate(data['statements'], 1):
                    required_fields = ['StatementNumber', 'StatementNumberPeriod', 'InitialBalanceValue', 
                                     'FinalBalanceValue', 'First Date', 'Last Date']
                    missing_fields = [field for field in required_fields if field not in stmt_data]
                    if missing_fields:
                        logger.error("Statement %d data: %s", idx, json.dumps(stmt_data, indent=2))
                        return HttpResponse(f"Error: Missing fields in statement {idx}: {missing_fields}", status=400)

                    statement, _ = Statement.objects.update_or_create(
                        statement_number=stmt_data['StatementNumber'],
                        defaults={
                            'period': stmt_data['StatementNumberPeriod'],
                            'initial_balance': stmt_data['InitialBalanceValue'],
                            'final_balance': stmt_data['FinalBalanceValue'],
                            'first_date': stmt_data['First Date'],
                            'last_date': stmt_data['Last Date'],
                        }
                    )

                    if 'DailySummaries' not in stmt_data:
                        logger.warning("Statement %d missing 'DailySummaries'. Skipping daily summaries.", idx)
                        continue

                    for daily_idx, daily_data in enumerate(stmt_data['DailySummaries'], 1):
                        daily_required_fields = ['Date', 'Debit', 'Credit', 'DailyFinalBalanceValue', 
                                               'Transaction Counts', 'DailyBalanceVerificiation']
                        daily_missing = [field for field in daily_required_fields if field not in daily_data]
                        if daily_missing:
                            return HttpResponse(f"Error: Missing fields in DailySummary {daily_idx} of Statement {idx}: {daily_missing}", status=400)

                        daily_summary, _ = DailySummary.objects.update_or_create(
                            statement=statement,
                            date=daily_data['Date'],
                            defaults={
                                'debit': daily_data['Debit'],
                                'credit': daily_data['Credit'],
                                'daily_final_balance': daily_data['DailyFinalBalanceValue'],
                                'transaction_count': daily_data['Transaction Counts'],
                                'balance_verified': daily_data['DailyBalanceVerificiation'],
                            }
                        )

                        if 'Transactions' not in daily_data:
                            logger.warning("DailySummary %d in Statement %d missing 'Transactions'. Skipping transactions.", daily_idx, idx)
                            continue

                        for trans_idx, trans_data in enumerate(daily_data['Transactions'], 1):
                            trans_required_fields = ['Debit', 'Credit', 'Value', 'ValueType', 'Date', 
                                                   'Table Body', 'IBAN Partner', 'InitialSold', 'FinalSold']
                            trans_missing = [field for field in trans_required_fields if field not in trans_data]
                            if trans_missing:
                                return HttpResponse(f"Error: Missing fields in Transaction {trans_idx} of DailySummary {daily_idx} in Statement {idx}: {trans_missing}", status=400)

                            Transaction.objects.update_or_create(
                                daily_summary=daily_summary,
                                date=trans_data['Date'],
                                value=trans_data['Value'],
                                value_type=trans_data['ValueType'],
                                defaults={
                                    'debit': trans_data['Debit'],
                                    'credit': trans_data['Credit'],
                                    'description': trans_data['Table Body'],
                                    'iban_partner': trans_data['IBAN Partner'] or None,
                                    'initial_sold': trans_data['InitialSold'],
                                    'final_sold': trans_data['FinalSold'],
                                    'partner_name': trans_data.get('Partner Name'),
                                    'transaction_type': trans_data.get('Transaction Type'),
                                    'reference': trans_data.get('Table Body', '').split('REF: ')[-1].split()[0] if 'REF: ' in trans_data.get('Table Body', '') else None,
                                }
                            )

            return HttpResponse("Import successful!", status=200)

        except json.JSONDecodeError as e:
            logger.error("JSON decode error: %s", str(e))
            return HttpResponse(f"Error: Invalid JSON format: {str(e)}", status=400)
        except Exception as e:
            logger.error("Unexpected error during import: %s", str(e))
            return HttpResponse(f"Error during import: {str(e)}", status=400)

    # Load all statements for the initial page load
    statements = Statement.objects.all()
    return render(request, 'import.html', {'statements': statements})

# AJAX endpoint to fetch daily summaries for a statement
def get_daily_summaries(request):
    statement_id = request.GET.get('statement_id')
    daily_summaries = DailySummary.objects.filter(statement_id=statement_id).values(
        'id', 'date', 'debit', 'credit', 'daily_final_balance', 'transaction_count', 'balance_verified'
    )
    return JsonResponse({'daily_summaries': list(daily_summaries)})

# AJAX endpoint to fetch transactions for a daily summary
def get_transactions(request):
    daily_summary_id = request.GET.get('daily_summary_id')
    transactions = Transaction.objects.filter(daily_summary_id=daily_summary_id).values(
        'date', 'debit', 'credit', 'value', 'value_type', 'description', 'iban_partner',
        'initial_sold', 'final_sold', 'partner_name', 'transaction_type', 'reference'
    )
    return JsonResponse({'transactions': list(transactions)})