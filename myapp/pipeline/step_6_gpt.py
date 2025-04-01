# 


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