# import json
# import csv

# # Deschide fișierul JSON
# with open('gpt-json-output.json', 'r', encoding='utf-8') as json_file:
#     data = json.load(json_file)

# # Definirea antetului pentru CSV (flatten pentru statement, rezumat zilnic și tranzacții)
# header = [
#     # Date din nivelul statementului
#     "StatementNumberPeriod",
#     "StatementNumber",
#     "InitialBalance",
#     "InitialBalanceValue",
#     "FinalBalance",
#     "FinalBalanceValue",
#     "First Date",
#     "Last Date",
#     # Date din rezumatul zilnic
#     "Daily Date",
#     "Daily Debit",
#     "Daily Credit",
#     "DailyFinalBalance",
#     "Transaction Counts",
#     "DailyFinalBalanceValue",
#     "DailyBalanceVerificiation",
#     # Date din tranzacție
#     "Transaction Index",
#     "Transaction Table Header",
#     "Transaction Table Body",
#     "Transaction Date",
#     "Transaction Debit",
#     "Transaction Credit",
#     "Transaction Value",
#     "Transaction ValueType",
#     "Transaction IBAN Partner",
#     "Transaction Partner Name",   # noua coloană
#     "Transaction Type",           # noua coloană
#     "Transaction InitialSold",
#     "Transaction FinalSold"
# ]

# # Deschide (sau creează) fișierul CSV de ieșire
# with open('gpt-output.csv', 'w', newline='', encoding='utf-8') as csv_file:
#     writer = csv.DictWriter(csv_file, fieldnames=header)
#     writer.writeheader()

#     # Parcurge fiecare statement
#     for statement in data.get("statements", []):
#         # Datele comune la nivelul statementului
#         statement_data = {
#             "StatementNumberPeriod": statement.get("StatementNumberPeriod", ""),
#             "StatementNumber": statement.get("StatementNumber", ""),
#             "InitialBalance": statement.get("InitialBalance", ""),
#             "InitialBalanceValue": statement.get("InitialBalanceValue", ""),
#             "FinalBalance": statement.get("FinalBalance", ""),
#             "FinalBalanceValue": statement.get("FinalBalanceValue", ""),
#             "First Date": statement.get("First Date", ""),
#             "Last Date": statement.get("Last Date", "")
#         }
        
#         # Parcurge fiecare rezumat zilnic
#         daily_summaries = statement.get("DailySummaries", [])
#         if daily_summaries:
#             for daily in daily_summaries:
#                 daily_data = {
#                     "Daily Date": daily.get("Date", ""),
#                     "Daily Debit": daily.get("Debit", ""),
#                     "Daily Credit": daily.get("Credit", ""),
#                     "DailyFinalBalance": daily.get("DailyFinalBalance", ""),
#                     "Transaction Counts": daily.get("Transaction Counts", ""),
#                     "DailyFinalBalanceValue": daily.get("DailyFinalBalanceValue", ""),
#                     "DailyBalanceVerificiation": daily.get("DailyBalanceVerificiation", "")
#                 }
                
#                 # Verifică dacă există tranzacții în cadrul rezumatului zilnic
#                 transactions = daily.get("Transactions", [])
#                 if transactions:
#                     for trans in transactions:
#                         transaction_data = {
#                             "Transaction Index": trans.get("Index", ""),
#                             "Transaction Table Header": trans.get("Table Header", ""),
#                             "Transaction Table Body": trans.get("Table Body", ""),
#                             "Transaction Date": trans.get("Date", ""),
#                             "Transaction Debit": trans.get("Debit", ""),
#                             "Transaction Credit": trans.get("Credit", ""),
#                             "Transaction Value": trans.get("Value", ""),
#                             "Transaction ValueType": trans.get("ValueType", ""),
#                             "Transaction IBAN Partner": trans.get("IBAN Partner", ""),
#                             "Transaction Partner Name": trans.get("Partner Name", ""),
#                             "Transaction Type": trans.get("Transaction Type", ""),
#                             "Transaction InitialSold": trans.get("InitialSold", ""),
#                             "Transaction FinalSold": trans.get("FinalSold", "")
#                         }
#                         # Combină datele la nivel de statement, daily și tranzacție
#                         row = {}
#                         row.update(statement_data)
#                         row.update(daily_data)
#                         row.update(transaction_data)
#                         writer.writerow(row)
#                 else:
#                     # Dacă nu există tranzacții în rezumatul zilnic, se completează câmpurile de tranzacție cu șiruri goale
#                     transaction_data = {
#                         "Transaction Index": "",
#                         "Transaction Table Header": "",
#                         "Transaction Table Body": "",
#                         "Transaction Date": "",
#                         "Transaction Debit": "",
#                         "Transaction Credit": "",
#                         "Transaction Value": "",
#                         "Transaction ValueType": "",
#                         "Transaction IBAN Partner": "",
#                         "Transaction Partner Name": "",
#                         "Transaction Type": "",
#                         "Transaction InitialSold": "",
#                         "Transaction FinalSold": ""
#                     }
#                     row = {}
#                     row.update(statement_data)
#                     row.update(daily_data)
#                     row.update(transaction_data)
#                     writer.writerow(row)
#         else:
#             # Dacă nu există rezumate zilnice, se completează și câmpurile aferente rezumatului și tranzacțiilor cu șiruri goale
#             daily_data = {
#                 "Daily Date": "",
#                 "Daily Debit": "",
#                 "Daily Credit": "",
#                 "DailyFinalBalance": "",
#                 "Transaction Counts": "",
#                 "DailyFinalBalanceValue": "",
#                 "DailyBalanceVerificiation": ""
#             }
#             transaction_data = {
#                 "Transaction Index": "",
#                 "Transaction Table Header": "",
#                 "Transaction Table Body": "",
#                 "Transaction Date": "",
#                 "Transaction Debit": "",
#                 "Transaction Credit": "",
#                 "Transaction Value": "",
#                 "Transaction ValueType": "",
#                 "Transaction IBAN Partner": "",
#                 "Transaction Partner Name": "",
#                 "Transaction Type": "",
#                 "Transaction InitialSold": "",
#                 "Transaction FinalSold": ""
#             }
#             row = {}
#             row.update(statement_data)
#             row.update(daily_data)
#             row.update(transaction_data)
#             writer.writerow(row)



# pipeline/step_7_gpt_csv.py
import json
import csv

csv_header = [
    "StatementNumberPeriod", "StatementNumber", "InitialBalance", "InitialBalanceValue",
    "FinalBalance", "FinalBalanceValue", "First Date", "Last Date",
    "Daily Date", "Daily Debit", "Daily Credit", "DailyFinalBalance",
    "Transaction Counts", "DailyFinalBalanceValue", "DailyBalanceVerificiation",
    "Transaction Index", "Transaction Table Header", "Transaction Table Body",
    "Transaction Date", "Transaction Debit", "Transaction Credit", "Transaction Value",
    "Transaction ValueType", "Transaction IBAN Partner", "Transaction Partner Name",
    "Transaction Type", "Transaction InitialSold", "Transaction FinalSold"
]

def convert_to_csv(input_json, output_csv):
    """Convert GPT-enhanced JSON to CSV."""
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
            daily_summaries = statement.get("DailySummaries", [])
            if daily_summaries:
                for daily in daily_summaries:
                    daily_data = {
                        "Daily Date": daily.get("Date", ""),
                        "Daily Debit": daily.get("Debit", ""),
                        "Daily Credit": daily.get("Credit", ""),
                        "DailyFinalBalance": daily.get("DailyFinalBalance", ""),
                        "Transaction Counts": daily.get("Transaction Counts", ""),
                        "DailyFinalBalanceValue": daily.get("DailyFinalBalanceValue", ""),
                        "DailyBalanceVerificiation": daily.get("DailyBalanceVerificiation", "")
                    }
                    transactions = daily.get("Transactions", [])
                    if transactions:
                        for trans in transactions:
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
                                "Transaction Partner Name": trans.get("Partner Name", ""),
                                "Transaction Type": trans.get("Transaction Type", ""),
                                "Transaction InitialSold": trans.get("InitialSold", ""),
                                "Transaction FinalSold": trans.get("FinalSold", "")
                            }
                            row = {**statement_data, **daily_data, **transaction_data}
                            writer.writerow(row)
                    else:
                        transaction_data = {
                            "Transaction Index": "", "Transaction Table Header": "", "Transaction Table Body": "",
                            "Transaction Date": "", "Transaction Debit": "", "Transaction Credit": "",
                            "Transaction Value": "", "Transaction ValueType": "", "Transaction IBAN Partner": "",
                            "Transaction Partner Name": "", "Transaction Type": "", "Transaction InitialSold": "",
                            "Transaction FinalSold": ""
                        }
                        row = {**statement_data, **daily_data, **transaction_data}
                        writer.writerow(row)
            else:
                daily_data = {
                    "Daily Date": "", "Daily Debit": "", "Daily Credit": "", "DailyFinalBalance": "",
                    "Transaction Counts": "", "DailyFinalBalanceValue": "", "DailyBalanceVerificiation": ""
                }
                transaction_data = {
                    "Transaction Index": "", "Transaction Table Header": "", "Transaction Table Body": "",
                    "Transaction Date": "", "Transaction Debit": "", "Transaction Credit": "",
                    "Transaction Value": "", "Transaction ValueType": "", "Transaction IBAN Partner": "",
                    "Transaction Partner Name": "", "Transaction Type": "", "Transaction InitialSold": "",
                    "Transaction FinalSold": ""
                }
                row = {**statement_data, **daily_data, **transaction_data}
                writer.writerow(row)