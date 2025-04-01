import re
import json
from datetime import datetime

def read_file(filename):
    """Citește întregul conținut al fișierului."""
    with open(filename, "r", encoding="utf-8") as f:
        return f.read()

def convert_date_format(date_str):
    """
    Convertește data din formatul dd/mm/yyyy (sau dd-mm-yyyy) în formatul yyyy-mm-dd.
    Dacă conversia eșuează, returnează șirul original.
    """
    try:
        # Înlocuim eventual separatorul '-' cu '/' pentru a standardiza
        date_str = date_str.replace("-", "/")
        dt = datetime.strptime(date_str, "%d/%m/%Y")
        return dt.strftime("%Y-%m-%d")
    except ValueError:
        return date_str

def extract_tag_content(text, tag):
    """
    Extrage textul dintr-un tag dat (ex: <tag> ... </tag>) din textul dat.
    Dacă tag-ul nu este găsit, returnează un șir gol.
    """
    pattern = r"<{tag}>(.*?)</{tag}>".format(tag=tag)
    match = re.search(pattern, text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return ""

def extract_statement_number(snp_text):
    """
    Extrage numărul statement-ului din textul din tag-ul statementNumberPeriod.
    De exemplu, din "EXTRAS CONT Numarul: 7 din 01/07/2024 - 31/07/2024" se extrage "7".
    Dacă nu se găsește un număr, returnează șirul gol.
    """
    match = re.search(r"numarul:\s*(\d+)", snp_text, re.IGNORECASE)
    if match:
        return match.group(1)
    return ""

def extract_balance_value(balance_text):
    """
    Extrage prima apariție a unui număr din textul unui balance.
    De exemplu, din "SOLD ANTERIOR 8,465.21" se extrage 8465.21.
    """
    match = re.search(r"(\d{1,3}(?:,\d{3})*(?:\.\d{2}))", balance_text)
    if match:
        value = match.group(1)
        try:
            return float(value.replace(",", ""))
        except ValueError:
            return 0.0
    return 0.0

def extract_value(tx_text):
    """
    Caută ultima apariție a unui număr cu separatori de mii și un separator decimal în textul unei tranzacții.
    Returnează valoarea ca float.
    """
    matches = re.findall(r"\d{1,3}(?:,\d{3})*(?:\.\d{2})", tx_text)
    if matches:
        try:
            return float(matches[-1].replace(",", ""))
        except ValueError:
            return 0.0
    return 0.0

def extract_date(tx_text):
    """
    Caută în textul tranzacției prima apariție a unei date în formatul dd/mm/yyyy sau dd-mm-yyyy
    și returnează data în formatul yyyy-mm-dd.
    """
    match = re.search(r"(\d{1,2}[/-]\d{1,2}[/-]\d{4})", tx_text)
    if match:
        return convert_date_format(match.group(1))
    return ""

def extract_first_last_dates(header_text):
    """
    Extrage toate datele din textul header-ului (din statementNumberPeriod)
    și returnează prima și ultima dată în formatul yyyy-mm-dd.
    Dacă se găsește doar o dată, ambele vor fi acea dată.
    """
    matches = re.findall(r"(\d{1,2}[/-]\d{1,2}[/-]\d{4})", header_text)
    if matches:
        dates = [convert_date_format(d) for d in matches]
        return dates[0], dates[-1]
    return "", ""

def determine_value_type(tx_text):
    """
    Metodă de rezervă pentru determinarea tipului valorii, dacă nu se identifică
    explicit prin contextul liniilor ("-"). Se folosește dacă nu s-au găsit
    valori Debit sau Credit conform noii logici.
    """
    lower = tx_text.lower()
    if "comision" in lower:
        return "Debit"
    elif "incasare" in lower:
        return "Credit"
    elif "plata" in lower:
        return "Debit"
    else:
        return "Debit"

def extract_iban(tx_text):
    """
    Caută un IBAN în textul tranzacției.
    Un IBAN tipic începe cu două litere, două cifre și continuă cu 10-30 de caractere alfanumerice.
    Returnează primul IBAN găsit sau un șir gol dacă nu se găsește.
    """
    pattern = r"\b[A-Z]{2}\d{2}[A-Z0-9]{10,30}\b"
    match = re.search(pattern, tx_text)
    if match:
        return match.group(0)
    return ""

def extract_transaction_amounts(tx_text):
    """
    Extragerea valorilor de Debit și Credit din textul unei tranzacții, bazându-se pe
    numărul de liniuţe (dash-uri) din apropierea valorii:
      - Dacă numărul este urmat de cel puțin 4 liniuţe (ex: "5.00-------"), acesta este Debit.
      - Dacă numărul este precedat de cel puțin 4 liniuţe (ex: "-------1,303.00"), acesta este Credit.
    Returnează un dicționar cu valorile ca numere.
    """
    debit_match = re.search(r"(\d{1,3}(?:,\d{3})*(?:\.\d{2}))([-]{4,})", tx_text)
    credit_match = re.search(r"([-]{4,})(\d{1,3}(?:,\d{3})*(?:\.\d{2}))", tx_text)
    
    debit_val = 0.0
    credit_val = 0.0
    
    if debit_match:
        try:
            debit_val = float(debit_match.group(1).replace(",", ""))
        except ValueError:
            debit_val = 0.0
    if credit_match:
        try:
            credit_val = float(credit_match.group(2).replace(",", ""))
        except ValueError:
            credit_val = 0.0
        
    if debit_val and credit_val:
        net = credit_val - debit_val
        if net > 0:
            value_type = "Credit"
        elif net < 0:
            value_type = "Debit"
        else:
            value_type = "Neutral"
        return {
            "Debit": debit_val,
            "Credit": credit_val,
            "Value": abs(net),
            "ValueType": value_type
        }
    elif debit_val:
        return {
            "Debit": debit_val,
            "Credit": 0.0,
            "Value": debit_val,
            "ValueType": "Debit"
        }
    elif credit_val:
        return {
            "Debit": 0.0,
            "Credit": credit_val,
            "Value": credit_val,
            "ValueType": "Credit"
        }
    else:
        value = extract_value(tx_text)
        return {
            "Debit": 0.0,
            "Credit": 0.0,
            "Value": value,
            "ValueType": determine_value_type(tx_text)
        }

def extract_daily_summary(summary_text):
    """
    Extrage informațiile dintr-un bloc <dailySummary>.
    Formatul așteptat:
      "dd/mm/yyyy RULAJ ZI <Debit> <Credit>
       SOLD FINAL ZI <DailyFinalBalance>"
    Returnează un dicționar cu valorile convertite la număr și data în format yyyy-mm-dd.
    """
    lines = summary_text.strip().splitlines()
    date, debit, credit, daily_final_balance = "", 0.0, 0.0, 0.0
    if lines:
        m = re.search(r"(\d{1,2}[/-]\d{1,2}[/-]\d{4})\s+RULAJ\s+ZI\s+([\d,]+\.\d{2})\s+([\d,]+\.\d{2})", lines[0])
        if m:
            date = convert_date_format(m.group(1))
            try:
                debit = float(m.group(2).replace(",", ""))
            except ValueError:
                debit = 0.0
            try:
                credit = float(m.group(3).replace(",", ""))
            except ValueError:
                credit = 0.0
        if len(lines) > 1:
            m2 = re.search(r"SOLD\s+FINAL\s+ZI\s+([\d,]+\.\d{2})", lines[1])
            if m2:
                try:
                    daily_final_balance = float(m2.group(1).replace(",", ""))
                except ValueError:
                    daily_final_balance = 0.0
    return {
        "Date": date,
        "Debit": debit,
        "Credit": credit,
        "DailyFinalBalance": daily_final_balance
    }

def parse_statements(text):
    """
    Parsează textul din fișierul step-4.txt și extrage blocurile de tip <statement>...</statement>.
    Fiecare statement va conține:
      - Informațiile header (statementNumberPeriod, statementInitialBalance etc.)
      - DailySummaries: o listă de grupuri, fiecare grup conținând:
           * Câmpurile extrase din blocul <dailySummary> (dacă există) sau calculate
           * "Transaction Counts": numărul de tranzacții din acel grup
           * "Transactions": lista tranzacțiilor din acel grup, ordonate cronologic
           * "DailyFinalBalanceValue": calculat prin parcurgerea tranzacțiilor din grup,
             pornind de la soldul de început al grupului (soldul final al grupului anterior
             sau, pentru primul grup, soldul inițial al statement‑ului) și adunând (cu semn plus)
             valoarea tranzacțiilor de tip Credit sau scăzând (cu semn minus) pe cele de tip Debit.
           * "DailyBalanceVerificiation": true dacă DailyFinalBalanceValue este egal cu
             DailyFinalBalance extras din bloc, altfel false.
    Soldurile se actualizează cumulativ.
    """
    statements = []
    statement_blocks = re.findall(r"<statement>(.*?)</statement>", text, re.DOTALL)
    
    for block in statement_blocks:
        snp = extract_tag_content(block, "statementNumberPeriod")
        statement_number = extract_statement_number(snp)
        init_bal = extract_tag_content(block, "statementInitialBalance")
        final_bal = extract_tag_content(block, "statementFinalBalance")
        first_date, last_date = extract_first_last_dates(snp)
        
        init_bal_value = extract_balance_value(init_bal)
        final_bal_value = extract_balance_value(final_bal)
        
        # Găsim toate intrările (tranzacții sau dailySummary) în ordinea apariției
        entry_pattern = re.compile(r"<(transaction|dailySummary)>(.*?)</\1>", re.DOTALL)
        entries = list(entry_pattern.finditer(block))
        
        daily_groups = []
        current_transactions = []
        group_debit_sum = 0.0
        group_credit_sum = 0.0
        # Soldul cumulativ (pentru întregul statement)
        cumulative_sold = init_bal_value
        # Soldul de început al grupului curent
        group_start_balance = cumulative_sold
        
        last_transaction_date = first_date
        
        for entry in entries:
            tag = entry.group(1)
            content = entry.group(2).strip()
            if tag == "transaction":
                tx = {}
                values = extract_transaction_amounts(content)
                tx.update(values)
                # Extrage data; dacă lipsește, se folosește ultima dată cunoscută
                tx_date = extract_date(content)
                if not tx_date:
                    tx_date = last_transaction_date
                else:
                    last_transaction_date = tx_date
                tx["Date"] = tx_date
                tx["Table Header"] = "Data Descriere  Debit Credit"
                tx["Table Body"] = " ".join(content.split())
                tx["IBAN Partner"] = extract_iban(content)
                # Indexul va fi atribuit ulterior, dar îl setăm ca int aici
                tx["Index"] = len(current_transactions) + 1
                
                tx_initial_sold = cumulative_sold
                try:
                    debit_val = float(tx["Debit"])
                except (ValueError, TypeError):
                    debit_val = 0.0
                try:
                    credit_val = float(tx["Credit"])
                except (ValueError, TypeError):
                    credit_val = 0.0
                final_sold = cumulative_sold - debit_val + credit_val
                tx["InitialSold"] = round(tx_initial_sold, 2)
                tx["FinalSold"] = round(final_sold, 2)
                cumulative_sold = final_sold
                
                # Actualizează sumele pentru grupul curent
                group_debit_sum += debit_val
                group_credit_sum += credit_val
                
                current_transactions.append(tx)
            elif tag == "dailySummary":
                ds = extract_daily_summary(content)
                ds["Transaction Counts"] = len(current_transactions)
                # Sortează tranzacțiile din grupul curent după Date și Index
                current_transactions.sort(key=lambda t: (t["Date"], t["Index"]))
                ds["Transactions"] = current_transactions.copy()
                # Dacă blocul dailySummary nu furnizează sume, le completăm cu cele calculate
                if ds["Debit"] == 0.0:
                    ds["Debit"] = round(group_debit_sum, 2)
                if ds["Credit"] == 0.0:
                    ds["Credit"] = round(group_credit_sum, 2)
                if ds["DailyFinalBalance"] == 0.0:
                    ds["DailyFinalBalance"] = round(cumulative_sold, 2)
                
                # Calculăm DailyFinalBalanceValue pentru acest grup:
                computed_final = group_start_balance + (group_credit_sum - group_debit_sum)
                ds["DailyFinalBalanceValue"] = round(computed_final, 2)
                # Verificare: true dacă computed_final este egal cu DailyFinalBalance (cu toleranță mică)
                ds["DailyBalanceVerificiation"] = abs(computed_final - ds["DailyFinalBalance"]) < 0.01
                
                daily_groups.append(ds)
                # Resetăm grupul curent
                current_transactions = []
                group_debit_sum = 0.0
                group_credit_sum = 0.0
                group_start_balance = computed_final
                if ds.get("Date"):
                    last_transaction_date = ds["Date"]
        
        # Dacă rămân tranzacții negrupate, le formăm ca grup final
        if current_transactions:
            final_group = {
                "Date": last_transaction_date,
                "Debit": round(group_debit_sum, 2),
                "Credit": round(group_credit_sum, 2),
                "DailyFinalBalance": round(cumulative_sold, 2),
                "Transaction Counts": len(current_transactions),
                "Transactions": current_transactions.copy()
            }
            computed_final = group_start_balance + (group_credit_sum - group_debit_sum)
            final_group["DailyFinalBalanceValue"] = round(computed_final, 2)
            final_group["DailyBalanceVerificiation"] = abs(computed_final - final_group["DailyFinalBalance"]) < 0.01
            daily_groups.append(final_group)
        
        # Sortează grupurile de daily summary după data grupului
        daily_groups.sort(key=lambda ds: ds["Date"])
        
        statement_dict = {
            "StatementNumberPeriod": snp,
            "StatementNumber": int(statement_number) if statement_number.isdigit() else statement_number,
            "InitialBalance": init_bal,
            "InitialBalanceValue": init_bal_value,
            "FinalBalance": final_bal,
            "FinalBalanceValue": final_bal_value,
            "First Date": first_date,
            "Last Date": last_date,
            "DailySummaries": daily_groups
        }
        
        statements.append(statement_dict)
    
    # Sortează statement-urile după StatementNumber și după First Date (care sunt în format yyyy-mm-dd)
    statements.sort(key=lambda s: (s["StatementNumber"] if isinstance(s["StatementNumber"], int) else 0, s["First Date"]))
    return statements

def process_output_txt_to_json(input_txt_path, final_json_path):
    """
    Citește fișierul step-4.txt, procesează conținutul pentru a extrage blocurile de tip statement
    și scrie rezultatul într-un fișier JSON structurat.
    """
    text = read_file(input_txt_path)
    statements = parse_statements(text)
    output_data = {"statements": statements}
    
    with open(final_json_path, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print(f"Fișierul '{final_json_path}' a fost creat cu succes!")

if __name__ == "__main__":
    input_txt = "step-3.txt"         # Fișierul de intrare (cu tag-uri)
    final_json = "json-output.json"    # Fișierul JSON de ieșire
    process_output_txt_to_json(input_txt, final_json)
