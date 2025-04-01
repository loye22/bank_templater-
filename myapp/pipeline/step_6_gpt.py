# import json
# import openai
# import time

# # Set your OpenAI API key (using the provided key)
# openai.api_key = "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"

# def extract_partner_info(table_header, table_body):
#     """
#     Creează un prompt pentru OpenAI pentru a extrage:
#       - numele partenerului ("Partner Name")
#       - tipul tranzacției ("Transaction Type")
    
#     Răspunsul trebuie să fie exact în format JSON, cu cele două chei.
#     """
#     prompt = f"""You have the following banking data:
# Table Header: {table_header}
# Table Body: {table_body}

# Based on these details, extract the partner information.
# Return your answer in exactly the following JSON format with no extra text:
# {{
#   "Partner Name": "<partner name>",
#   "Transaction Type": "<transaction type>"
# }}
# Exist only 5 variants for "Transaction Type": "Bank Transfer", "Comision", "Retragere Numerar","Depunere Numerar", "POS". You can only answear with one of them.
# The banking data has been parsed from a PDF Account Statement from Banca Transilvania.
# Ensure the result is valid JSON.
# """
#     # Nu mai afișăm promptul sau răspunsul API în terminal
#     try:
#         response = openai.ChatCompletion.create(
#             model="gpt-4o-mini",  # Înlocuiește cu modelul disponibil, dacă e necesar
#             messages=[
#                 {
#                     "role": "system",
#                     "content": "You are a helpful assistant that responds ONLY in valid JSON format with no extra text."
#                 },
#                 {"role": "user", "content": prompt}
#             ],
#             temperature=0.0,
#             max_tokens=200
#         )
#         answer = response["choices"][0]["message"]["content"].strip()
#         data = json.loads(answer)
#         return data
#     except Exception as e:
#         return {"Partner Name": "", "Transaction Type": ""}

# def main():
#     print("Loading file json-output.json...")
#     try:
#         with open("json-output.json", "r", encoding="utf-8") as infile:
#             data = json.load(infile)
#     except Exception as e:
#         print(f"Error loading json-output.json: {e}")
#         return

#     print("File loaded. Processing transactions...")

#     # Calculează numărul total de tranzacții
#     total_transactions = 0
#     for statement in data.get("statements", []):
#         for daily_summary in statement.get("DailySummaries", []):
#             total_transactions += len(daily_summary.get("Transactions", []))
    
#     print(f"Total transactions: {total_transactions}")
#     processed_count = 0

#     # Parcurge fiecare statement, daily summary și tranzacție
#     for statement in data.get("statements", []):
#         for daily_summary in statement.get("DailySummaries", []):
#             for transaction in daily_summary.get("Transactions", []):
#                 table_header = transaction.get("Table Header", "")
#                 table_body = transaction.get("Table Body", "")
#                 # Apelează API-ul pentru extragerea informațiilor partenerului
#                 result = extract_partner_info(table_header, table_body)
#                 transaction["Partner Name"] = result.get("Partner Name", "")
#                 transaction["Transaction Type"] = result.get("Transaction Type", "")
#                 processed_count += 1
#                 print(f"Completed {processed_count}/{total_transactions}")
#                 time.sleep(1)  # Pauză pentru a evita limitarea ratei

#     print("All transactions processed. Saving file gpt-json-output.json...")
#     try:
#         with open("gpt-json-output.json", "w", encoding="utf-8") as outfile:
#             json.dump(data, outfile, ensure_ascii=False, indent=2)
#         print("File gpt-json-output.json has been created successfully.")
#     except Exception as e:
#         print(f"Error saving gpt-json-output.json: {e}")

# if __name__ == "__main__":
#     main()

############################################################################################
# pipeline/step_6_gpt.py
# import json
# import openai
# import time

# def process_with_gpt(input_json, output_json):
#     """
#     Process JSON with GPT to extract Partner Name and Transaction Type.
#     Prints progress to terminal and logs errors.
#     """
#     with open(input_json, "r", encoding="utf-8") as infile:
#         data = json.load(infile)

#     total_transactions = 0
#     for statement in data.get("statements", []):
#         for daily_summary in statement.get("DailySummaries", []):
#             total_transactions += len(daily_summary.get("Transactions", []))
#     print(f"Total transactions to process: {total_transactions}")

#     processed_count = 0
#     for statement in data.get("statements", []):
#         for daily_summary in statement.get("DailySummaries", []):
#             for transaction in daily_summary.get("Transactions", []):
#                 table_header = transaction.get("Table Header", "")
#                 table_body = transaction.get("Table Body", "")
#                 prompt = f"""You have the following banking data:
# Table Header: {table_header}
# Table Body: {table_body}
# Based on these details, extract the partner information.
# Return your answer in exactly the following JSON format with no extra text:
# {{
#   "Partner Name": "<partner name>",
#   "Transaction Type": "<transaction type>"
# }}
# Exist only 5 variants for "Transaction Type": "Bank Transfer", "Comision", "Retragere Numerar","Depunere Numerar", "POS".
# """
#                 try:
#                     response = openai.ChatCompletion.create(
#                         model="gpt-4o-mini",
#                         messages=[
#                             {"role": "system", "content": "Respond ONLY in valid JSON format."},
#                             {"role": "user", "content": prompt}
#                         ],
#                         temperature=0.0,
#                         max_tokens=200
#                     )
#                     result = json.loads(response["choices"][0]["message"]["content"].strip())
#                     transaction["Partner Name"] = result.get("Partner Name", "")
#                     transaction["Transaction Type"] = result.get("Transaction Type", "")
#                 except Exception as e:
#                     print(f"Error processing transaction {processed_count + 1}/{total_transactions}: {e}")
#                     transaction["Partner Name"] = ""
#                     transaction["Transaction Type"] = ""
                
#                 processed_count += 1
#                 print(f"Completed {processed_count}/{total_transactions}")
#                 time.sleep(1)  # Rate limiting

#     with open(output_json, "w", encoding="utf-8") as outfile:
#         json.dump(data, outfile, ensure_ascii=False, indent=2)
#     print("All transactions processed.")


######################################################################################


# pipeline/step_6_gpt.py
import json
import openai
import time

def process_with_gpt(input_json, output_json):
    """
    Process JSON with GPT to extract Partner Name and Transaction Type.
    Prints progress to terminal and logs errors.
    """
    with open(input_json, "r", encoding="utf-8") as infile:
        data = json.load(infile)

    total_transactions = 0
    for statement in data.get("statements", []):
        for daily_summary in statement.get("DailySummaries", []):
            total_transactions += len(daily_summary.get("Transactions", []))
    print(f"Total transactions to process: {total_transactions}")

    processed_count = 0
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
                except Exception as e:
                    print(f"Error processing transaction {processed_count + 1}/{total_transactions}: {e}")
                    transaction["Partner Name"] = ""
                    transaction["Transaction Type"] = ""
                
                processed_count += 1
                print(f"Completed {processed_count}/{total_transactions}")
                time.sleep(1)  # Rate limiting

    with open(output_json, "w", encoding="utf-8") as outfile:
        json.dump(data, outfile, ensure_ascii=False, indent=2)
    print("All transactions processed.")