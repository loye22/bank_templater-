def process_file(input_path, output_path):
    """
    Acest script procesează fișierul 'final_export.txt' și înlocuiește markerii cu tag-uri XML.
    Tag-ul <transaction> este introdus doar pentru blocurile de tranzacții (adică în afara secțiunilor
    precum <statement>, <statementNumberPeriod>, <statementInfo>, <statementInitialBalance>, 
    <statementFinalBalance> și <dailySummary>). La final se elimină blocurile de tranzacție care nu conțin "REF:".
    """
    result_lines = []
    current_section = None  # Indică secțiunea curentă (ex.: "statement", "statementNumberPeriod", etc.)
    in_transaction = False  # Flag pentru blocul de tranzacție deschis

    with open(input_path, "r", encoding="utf-8") as f:
        for line in f:
            stripped_line = line.rstrip("\n")
            
            # Verificăm dacă linia este un marker cunoscut
            if stripped_line in {
                "=== STATEMENT START ===",
                "=== STATEMENT NUMBER & PERIOD START ===",
                "=== STATEMENT INFO START ===",
                "=== STATEMENT INITIAL BALANCE START ===",
                "=== STATEMENT FINAL BALANCE START ===",
                "=== DAILY SUMMARY START ===",
                "=== STATEMENT END ===",
                "=== STATEMENT NUMBER & PERIOD END ===",
                "=== STATEMENT INFO END ===",
                "=== STATEMENT INITIAL BALANCE END ===",
                "=== STATEMENT FINAL BALANCE END ===",
                "=== DAILY SUMMARY END ===",
                "=== TRANSACTION END ==="
            }:
                # Dacă avem o tranzacție deschisă și markerul actual nu este cel de finalizare a tranzacției,
                # închidem blocul de tranzacție
                if in_transaction and stripped_line != "=== TRANSACTION END ===":
                    result_lines.append("</transaction>")
                    in_transaction = False
                
                # Markerii de START pentru secțiuni
                if stripped_line == "=== STATEMENT START ===":
                    result_lines.append("<statement>")
                    current_section = "statement"
                    continue
                elif stripped_line == "=== STATEMENT NUMBER & PERIOD START ===":
                    result_lines.append("<statementNumberPeriod>")
                    current_section = "statementNumberPeriod"
                    continue
                elif stripped_line == "=== STATEMENT INFO START ===":
                    result_lines.append("<statementInfo>")
                    current_section = "statementInfo"
                    continue
                elif stripped_line == "=== STATEMENT INITIAL BALANCE START ===":
                    result_lines.append("<statementInitialBalance>")
                    current_section = "statementInitialBalance"
                    continue
                elif stripped_line == "=== STATEMENT FINAL BALANCE START ===":
                    result_lines.append("<statementFinalBalance>")
                    current_section = "statementFinalBalance"
                    continue
                elif stripped_line == "=== DAILY SUMMARY START ===":
                    result_lines.append("<dailySummary>")
                    current_section = "dailySummary"
                    continue

                # Markerii de END pentru secțiuni
                elif stripped_line == "=== STATEMENT END ===":
                    result_lines.append("</statement>")
                    current_section = None
                    continue
                elif stripped_line == "=== STATEMENT NUMBER & PERIOD END ===":
                    result_lines.append("</statementNumberPeriod>")
                    current_section = None
                    continue
                elif stripped_line == "=== STATEMENT INFO END ===":
                    result_lines.append("</statementInfo>")
                    current_section = None
                    continue
                elif stripped_line == "=== STATEMENT INITIAL BALANCE END ===":
                    result_lines.append("</statementInitialBalance>")
                    current_section = None
                    continue
                elif stripped_line == "=== STATEMENT FINAL BALANCE END ===":
                    result_lines.append("</statementFinalBalance>")
                    current_section = None
                    continue
                elif stripped_line == "=== DAILY SUMMARY END ===":
                    result_lines.append("</dailySummary>")
                    current_section = None
                    continue
                elif stripped_line == "=== TRANSACTION END ===":
                    # Încheiem blocul de tranzacție doar dacă era deschis
                    if in_transaction:
                        result_lines.append("</transaction>")
                        in_transaction = False
                    else:
                        result_lines.append("</transaction>")
                    continue

            # Linia nu este marker
            if current_section is None:
                # Suntem în zona de tranzacții (în afara secțiunilor definite)
                if stripped_line.strip() != "" and not in_transaction:
                    # Deschidem blocul de tranzacție doar dacă linia nu e goală și nu avem bloc deschis
                    result_lines.append("<transaction>")
                    in_transaction = True
                result_lines.append(stripped_line)
            else:
                # Dacă suntem în interiorul unei secțiuni, nu adăugăm tag-ul <transaction>
                result_lines.append(stripped_line)
    
    # Închidem orice tranzacție deschisă la finalul fișierului
    if in_transaction:
        result_lines.append("</transaction>")

    # Filtrăm blocurile de tranzacție care nu conțin "REF:"
    filtered_lines = filter_transactions(result_lines)

    with open(output_path, "w", encoding="utf-8") as outf:
        outf.write("\n".join(filtered_lines))
    
    print(f"Fișierul '{output_path}' a fost creat cu succes!")


def filter_transactions(lines):
    """
    Parcurge lista de linii și elimină blocurile <transaction>...</transaction>
    care nu conțin "REF:" în conținutul lor.
    """
    filtered_lines = []
    inside_transaction = False
    transaction_block = []
    
    for line in lines:
        if line.strip() == "<transaction>":
            inside_transaction = True
            transaction_block = [line]
        elif line.strip() == "</transaction>" and inside_transaction:
            transaction_block.append(line)
            # Verificăm dacă blocul de tranzacție conține "REF:"
            block_content = "\n".join(transaction_block)
            if "REF:" in block_content:
                filtered_lines.extend(transaction_block)
            # Dacă nu, blocul este omis (nu se adaugă nimic)
            inside_transaction = False
            transaction_block = []
        elif inside_transaction:
            transaction_block.append(line)
        else:
            filtered_lines.append(line)
    
    # Dacă, din orice motiv, un bloc de tranzacție nu s-a închis, îl adăugăm doar dacă conține "REF:"
    if inside_transaction:
        block_content = "\n".join(transaction_block)
        if "REF:" in block_content:
            filtered_lines.extend(transaction_block)
    
    return filtered_lines


if __name__ == "__main__":
    input_file = "step-2.txt"   # Calea către fișierul de intrare
    output_file = "step-3.txt"    # Calea către fișierul de ieșire
    process_file(input_file, output_file)
