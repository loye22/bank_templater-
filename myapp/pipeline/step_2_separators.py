def transform_export(input_path, output_path):
    """
    1) Remove all blocks from 'BANCA TRANSILVANIA' up to a line containing 'Tiparit:' (inclusive).
    2) Remove the block 'BANCA TRANSILVANIA S.A. ... Capital...' up to 'www.bancatransilvania.ro' (inclusive).
    3) Insert/remove lines according to your tagging rules (STATEMENT, TRANSACTION, DAILY SUMMARY, etc.).
    4) 'SOLD ANTERIOR' => wrap only that line with STATEMENT INITIAL BALANCE START/END.
    5) 'SOLD FINAL CONT' => wrap only that line with STATEMENT FINAL BALANCE START/END.
    6) Keep 'Data Descriere  Debit Credit' only if the previous line is exactly
       'RON Cod IBAN: RO32BTRLRONCRT0610707201'. Otherwise remove it.
    7) Add a blank line below each '...END ===' and a blank line above each '...START ==='.
    8) At the end, remove a possible '=== STATEMENT END ===' at the very start,
       and finally add a single '=== STATEMENT END ===' line at the very end.
    """

    # --- STEP 1: READ ALL LINES ---
    with open(input_path, 'r', encoding='utf-8') as f:
        original_lines = f.readlines()

    # --- STEP A: REMOVE BLOCKS FROM "BANCA TRANSILVANIA" TO "Tiparit:" ---
    lines_no_banca = []
    i = 0
    n = len(original_lines)
    while i < n:
        line = original_lines[i]
        if line.strip() == "BANCA TRANSILVANIA":
            # Skip until we find a line containing "Tiparit:"
            i += 1
            while i < n:
                if "Tiparit:" in original_lines[i]:
                    i += 1  # remove that line as well
                    break
                i += 1
            # Optionally remove extra blank line
            if i < n and not original_lines[i].strip():
                i += 1
            continue
        else:
            lines_no_banca.append(line)
            i += 1

    # --- STEP B: REMOVE "BANCA TRANSILVANIA S.A. ... CAPITAL..." BLOCK UNTIL "www.bancatransilvania.ro" ---
    final_lines = []
    i = 0
    n = len(lines_no_banca)
    while i < n:
        line = lines_no_banca[i]
        if (
            "BANCA TRANSILVANIA S.A." in line
            and ("Capital" in line or "Capitalul" in line)
        ):
            i += 1
            while i < n:
                if "www.bancatransilvania.ro" in lines_no_banca[i]:
                    i += 1
                    break
                i += 1
            continue
        else:
            final_lines.append(line)
            i += 1

    # --- STEP C: APPLY INSERTION/REMOVAL RULES ---
    result_lines = []
    i = 0
    n = len(final_lines)

    while i < n:
        line = final_lines[i]

        # RULE 1) "SEPTEM GENERATION Client: 6107072" + next line "CUI: 15739223"
        if i + 1 < n:
            if (
                line.strip().startswith("SEPTEM GENERATION Client: 6107072")
                and final_lines[i+1].strip().startswith("CUI: 15739223")
            ):
                result_lines.append("=== STATEMENT END ===\n")
                result_lines.append("\n")  # blank line after END
                result_lines.append("\n")  # blank line before START
                result_lines.append("=== STATEMENT START ===\n")
                result_lines.append(line)
                result_lines.append(final_lines[i+1])
                i += 2
                continue

        # RULE 2) WRAP "EXTRAS CONT Numarul:" WITH START/END + BLANK LINES
        if "EXTRAS CONT Numarul:" in line:
            result_lines.append("\n")  # blank line above
            result_lines.append("=== STATEMENT NUMBER & PERIOD START ===\n")
            result_lines.append(line)
            result_lines.append("=== STATEMENT NUMBER & PERIOD END ===\n")
            result_lines.append("\n")  # blank line below
            i += 1
            continue

        # RULE 3) STATEMENT INFO BLOCK (3 lines):
        if (
            i + 2 < n
            and line.strip().startswith("CONT 045RONCRT0610707201 Valuta Cont de disponibil")
            and "RON Cod IBAN: RO32BTRLRONCRT0610707201" in final_lines[i+1]
            and "Data Descriere  Debit Credit" in final_lines[i+2]
        ):
            result_lines.append("\n")
            result_lines.append("=== STATEMENT INFO START ===\n")
            result_lines.append(line)
            result_lines.append(final_lines[i+1])
            result_lines.append(final_lines[i+2])
            result_lines.append("=== STATEMENT INFO END ===\n")
            result_lines.append("\n")
            i += 3
            continue

        # RULE 4) "SOLD ANTERIOR" => WRAP ONLY THAT LINE
        if "SOLD ANTERIOR" in line:
            result_lines.append("\n")
            result_lines.append("=== STATEMENT INITIAL BALANCE START ===\n")
            result_lines.append(line)
            result_lines.append("=== STATEMENT INITIAL BALANCE END ===\n")
            result_lines.append("\n")
            i += 1
            continue

        # RULE 5) "SOLD FINAL CONT" => WRAP ONLY THAT LINE
        if "SOLD FINAL CONT" in line:
            result_lines.append("\n")
            result_lines.append("=== STATEMENT FINAL BALANCE START ===\n")
            result_lines.append(line)
            result_lines.append("=== STATEMENT FINAL BALANCE END ===\n")
            result_lines.append("\n")
            i += 1
            continue

        # RULE 6) "Data Descriere  Debit Credit" => keep only if prev line is the IBAN line
        if line.strip() == "Data Descriere  Debit Credit":
            if (
                len(result_lines) > 0
                and result_lines[-1].strip() == "RON Cod IBAN: RO32BTRLRONCRT0610707201"
            ):
                # keep
                result_lines.append(line)
            i += 1
            continue

        # RULE 7) ANY LINE WITH "REF:" => add "=== TRANSACTION END ===" + BLANK LINE
        if "REF:" in line:
            result_lines.append(line)
            result_lines.append("=== TRANSACTION END ===\n")
            result_lines.append("\n")
            i += 1
            continue

        # RULE 8) DAILY SUMMARY => "RULAJ ZI"
        if "RULAJ ZI" in line:
            result_lines.append("\n")  # blank line above
            result_lines.append("=== DAILY SUMMARY START ===\n")
            result_lines.append(line)
            i += 1
            if i < n and "SOLD FINAL ZI" in final_lines[i]:
                result_lines.append(final_lines[i])
                result_lines.append("=== DAILY SUMMARY END ===\n")
                result_lines.append("\n")
                i += 1
            continue

        # DEFAULT: KEEP THE LINE
        result_lines.append(line)
        i += 1

    # --- STEP D: REMOVE A POSSIBLE "=== STATEMENT END ===" AT THE VERY START ---
    clean_result = []
    idx = 0
    # Skip leading blank lines
    while idx < len(result_lines) and not result_lines[idx].strip():
        idx += 1
    # If the first non-empty line is "=== STATEMENT END ===", remove it
    if idx < len(result_lines) and result_lines[idx].strip() == "=== STATEMENT END ===":
        idx += 1
        # Also skip subsequent blank lines if we want
        while idx < len(result_lines) and not result_lines[idx].strip():
            idx += 1

    # Now copy the remainder
    clean_result.extend(result_lines[idx:])

    # --- STEP E: ADD A FINAL "=== STATEMENT END ===" ---
    # (You can optionally add a blank line before if desired.)
    clean_result.append("=== STATEMENT END ===\n")

    # --- STEP F: WRITE EVERYTHING ---
    with open(output_path, 'w', encoding='utf-8') as f:
        f.writelines(clean_result)

def main():
    input_file = "step-1.txt"
    output_file = "step-2.txt"
    transform_export(input_file, output_file)
    print(f"Processed file saved to: {output_file}")

if __name__ == "__main__":
    main()
