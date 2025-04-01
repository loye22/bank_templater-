import logging
import json
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.db import transaction
from .models import Statement, DailySummary, Transaction
from .models import ProcessedFile

logger = logging.getLogger(__name__)

def processed_files(request):
    if request.method == 'POST':
        # Handle PDF file upload
        pdf_file = request.FILES.get('pdf_file')
        if pdf_file:
            processed_file = ProcessedFile(file=pdf_file)
            processed_file.save()
            # Add your PDF processing logic here
    
    files = ProcessedFile.objects.all().order_by('-processed_at')
    return render(request, 'processed_files.html', {'processed_files': files})

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
###########################################################################
import os
import tempfile
import openai
import json
import time
from django.shortcuts import render
from django.core.files import File
from .models import ProcessedFile
from django.conf import settings
import csv
import re
import sys
sys.path.append(os.path.abspath('../pipeline'))  # Adjust the path if needed

# Import pipeline functions using your style
from .pipeline import step_2_separators
from .pipeline import step_3_tags
from .pipeline import step_4_json
from .pipeline import step_5_convert_csv
from .pipeline import step_6_gpt
from .pipeline import step_7_gpt_csv

# Configure OpenAI API key (use environment variable for security)
openai.api_key = os.getenv("OPENAI_API_KEY", "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")

def run_steps_1_to_7(pdf_path):
    """
    Execute Steps 1-7, including GPT enhancement and final CSV conversion.
    Returns paths to gpt-json-output.json and gpt-output.csv.
    """
    base_dir = tempfile.mkdtemp()
    print(f"Created temp directory: {base_dir}")
    
    # Step 1: Extract text from PDF
    step1_output = os.path.join(base_dir, "step-1.txt")
    with open(pdf_path, 'rb') as pdf_file, open(step1_output, 'w', encoding='utf-8') as f:
        from PyPDF2 import PdfReader
        reader = PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                page_text = re.sub(r'( {2,})', lambda m: '-' * len(m.group(0)), page_text)
                text += page_text + "\n"
        f.write(text)
    print("Step 1 completed: PDF text extracted")
    
    # Step 2: Transform text
    step2_output = os.path.join(base_dir, "step-2.txt")
    step_2_separators.transform_export(step1_output, step2_output)
    print("Step 2 completed: Text transformed")
    
    # Step 3: Add tags
    step3_output = os.path.join(base_dir, "step-3.txt")
    step_3_tags.process_file(step2_output, step3_output)
    print("Step 3 completed: Tags added")
    
    # Step 4: Convert to JSON
    json_output = os.path.join(base_dir, "json-output.json")
    step_4_json.process_output_txt_to_json(step3_output, json_output)
    print("Step 4 completed: JSON created")
    
    # Step 5: Convert to CSV
    csv_output = os.path.join(base_dir, "output.csv")
    step_5_convert_csv.convert_to_csv(json_output, csv_output)
    print("Step 5 completed: CSV created")
    
    # Step 6: Enhance with GPT
    gpt_json_output = os.path.join(base_dir, "gpt-json-output.json")
    print("Starting Step 6: GPT enhancement")
    step_6_gpt.process_with_gpt(json_output, gpt_json_output)
    print("Step 6 completed: GPT-enhanced JSON created")
    
    # Step 7: Convert GPT JSON to CSV
    gpt_csv_output = os.path.join(base_dir, "gpt-output.csv")
    step_7_gpt_csv.convert_to_csv(gpt_json_output, gpt_csv_output)
    print("Step 7 completed: GPT-enhanced CSV created")
    
    return gpt_json_output, gpt_csv_output

def processed_files(request):
    if request.method == 'POST':
        pdf_file = request.FILES.get('pdf_file')
        if pdf_file:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
                tmp.write(pdf_file.read())
                pdf_path = tmp.name

            step1_output = None
            step2_output = None
            step3_output = None
            json_output = None
            csv_output = None
            gpt_json_output = None
            gpt_csv_output = None

            try:
                gpt_json_output, gpt_csv_output = run_steps_1_to_7(pdf_path)
                step1_output = os.path.join(os.path.dirname(gpt_json_output), "step-1.txt")
                step2_output = os.path.join(os.path.dirname(gpt_json_output), "step-2.txt")
                step3_output = os.path.join(os.path.dirname(gpt_json_output), "step-3.txt")
                json_output = os.path.join(os.path.dirname(gpt_json_output), "json-output.json")
                csv_output = os.path.join(os.path.dirname(gpt_json_output), "output.csv")

                # Save Step 6 output
                with open(gpt_json_output, 'rb') as f:
                    processed_file = ProcessedFile(
                        file=File(f, name="gpt-json-output.json"),
                        description="Step 6: GPT-enhanced JSON output"
                    )
                    processed_file.save()
                print("Step 6 output saved to database")

                # Save Step 7 output
                with open(gpt_csv_output, 'rb') as f:
                    processed_file = ProcessedFile(
                        file=File(f, name="gpt-output.csv"),
                        description="Step 7: GPT-enhanced CSV output"
                    )
                    processed_file.save()
                print("Step 7 output saved to database")

            except Exception as e:
                print(f"Error during processing: {e}")
                raise

            finally:
                if os.path.exists(pdf_path):
                    os.remove(pdf_path)
                if step1_output and os.path.exists(step1_output):
                    os.remove(step1_output)
                if step2_output and os.path.exists(step2_output):
                    os.remove(step2_output)
                if step3_output and os.path.exists(step3_output):
                    os.remove(step3_output)
                if json_output and os.path.exists(json_output):
                    os.remove(json_output)
                if csv_output and os.path.exists(csv_output):
                    os.remove(csv_output)
                if gpt_json_output and os.path.exists(gpt_json_output):
                    os.remove(gpt_json_output)
                if gpt_csv_output and os.path.exists(gpt_csv_output):
                    os.remove(gpt_csv_output)
                    temp_dir = os.path.dirname(gpt_csv_output)
                    if os.path.exists(temp_dir):
                        os.rmdir(temp_dir)
                print("Temporary files cleaned up")

    files = ProcessedFile.objects.all().order_by('-processed_at')
    return render(request, 'processed_files.html', {'processed_files': files})

# Keep these for reference
def process_with_gpt(input_json, output_json):
    with open(input_json, "r", encoding="utf-8") as infile:
        data = json.load(infile)
    for statement in data.get("statements", []):
        for daily_summary in statement.get("DailySummaries", []):
            for transaction in daily_summary.get("Transactions", []):
                table_header = transaction.get("Table Header", "")
                table_body = transaction.get("Table Body", "")
                prompt = f"""You have the following banking data:
Table Header: {table_header}
Table Body: {table_body}
Based on these details, extract the partner information.
Return your answer in exactly the following JSON format with no extra text:
{{
  "Partner Name": "<partner name>",
  "Transaction Type": "<transaction type>"
}}
Exist only 5 variants for "Transaction Type": "Bank Transfer", "Comision", "Retragere Numerar","Depunere Numerar", "POS".
"""
                try:
                    response = openai.ChatCompletion.create(
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "system", "content": "Respond ONLY in valid JSON format."},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.0,
                        max_tokens=200
                    )
                    result = json.loads(response["choices"][0]["message"]["content"].strip())
                    transaction["Partner Name"] = result.get("Partner Name", "")
                    transaction["Transaction Type"] = result.get("Transaction Type", "")
                    time.sleep(1)
                except Exception:
                    transaction["Partner Name"] = ""
                    transaction["Transaction Type"] = ""
    with open(output_json, "w", encoding="utf-8") as outfile:
        json.dump(data, outfile, ensure_ascii=False, indent=2)

def convert_to_csv(input_json, output_csv):
    with open(input_json, 'r', encoding='utf-8') as json_file:
        data = json.load(json_file)
    with open(output_csv, 'w', newline='', encoding='utf-8') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=csv_header)
        writer.writeheader()
        for statement in data.get("statements", []):
            statement_data = {
                "StatementNumberPeriod": statement.get("StatementNumberPeriod", ""),
                "StatementNumber": statement.get("StatementNumber", ""),
                "InitialBalance": statement.get("InitialBalance", ""),
                "InitialBalanceValue": statement.get("InitialBalanceValue", ""),
                "FinalBalance": statement.get("FinalBalance", ""),
                "FinalBalanceValue": statement.get("FinalBalanceValue", ""),
                "First Date": statement.get("First Date", ""),
                "Last Date": statement.get("Last Date", "")
            }
            for daily in statement.get("DailySummaries", []):
                daily_data = {
                    "Daily Date": daily.get("Date", ""),
                    "Daily Debit": daily.get("Debit", ""),
                    "Daily Credit": daily.get("Credit", ""),
                    "DailyFinalBalance": daily.get("DailyFinalBalance", ""),
                    "Transaction Counts": daily.get("Transaction Counts", ""),
                    "DailyFinalBalanceValue": daily.get("DailyFinalBalanceValue", ""),
                    "DailyBalanceVerificiation": daily.get("DailyBalanceVerificiation", "")
                }
                for trans in daily.get("Transactions", []):
                    transaction_data = {
                        "Transaction Index": trans.get("Index", ""),
                        "Transaction Table Header": trans.get("Table Header", ""),
                        "Transaction Table Body": trans.get("Table Body", ""),
                        "Transaction Date": trans.get("Date", ""),
                        "Transaction Debit": trans.get("Debit", ""),
                        "Transaction Credit": trans.get("Credit", ""),
                        "Transaction Value": trans.get("Value", ""),
                        "Transaction ValueType": trans.get("ValueType", ""),
                        "Transaction IBAN Partner": trans.get("IBAN Partner", ""),
                        "Transaction InitialSold": trans.get("InitialSold", ""),
                        "Transaction FinalSold": trans.get("FinalSold", "")
                    }
                    row = {**statement_data, **daily_data, **transaction_data}
                    writer.writerow(row)
                if not daily.get("Transactions", []):
                    transaction_data = {f"Transaction {k}": "" for k in ["Index", "Table Header", "Table Body", "Date", "Debit", "Credit", "Value", "ValueType", "IBAN Partner", "InitialSold", "FinalSold"]}
                    row = {**statement_data, **daily_data, **transaction_data}
                    writer.writerow(row)