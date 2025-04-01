import PyPDF2
import os
import re

def extract_text_from_pdf(pdf_path):
    """
    Extrage textul dintr-un fișier PDF și înlocuiește secvențele de spații multiple 
    (2 sau mai multe) cu același număr de caractere '-' pentru a accentua delimitatorii.
    
    :param pdf_path: Calea către fișierul PDF
    :return: Textul extras ca șir de caractere
    """
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    # Înlocuiește orice secvență de 2 sau mai multe spații cu '-' repetat de același număr
                    page_text = re.sub(r'( {2,})', lambda m: '-' * len(m.group(0)), page_text)
                    text += page_text + "\n"
            return text
    except Exception as e:
        print(f"Eroare la citirea PDF: {e}")
        return None

if __name__ == "__main__":
    # Fișierul PDF sursă și fișierul de export
    pdf_file = "test.pdf"
    export_file = "step-1.txt"

    # Verificăm existența fișierului PDF
    if os.path.exists(pdf_file):
        extracted_text = extract_text_from_pdf(pdf_file)
        if extracted_text:
            try:
                with open(export_file, "w", encoding="utf-8") as f:
                    f.write(extracted_text)
                print(f"Textul a fost exportat cu succes în '{export_file}'.")
            except Exception as e:
                print(f"Eroare la salvarea fișierului: {e}")
        else:
            print("Nu s-a putut extrage textul din fișier.")
    else:
        print(f"Fișierul {pdf_file} nu există în directorul curent.")
