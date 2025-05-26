import pandas as pd
import numpy as np
import os
import seaborn as sns
import matplotlib.pyplot as plt
from fpdf import FPDF
import tempfile
import matplotlib
matplotlib.use('Agg')
import unicodedata
from datetime import datetime
from django.utils.text import slugify  # ✅ Pour nom de fichier

# ✅ Créer le dossier automatiquement si nécessaire
PDF_OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'pdf_generated_popmetre')
os.makedirs(PDF_OUTPUT_DIR, exist_ok=True)

def clean_text(text):
    replacements = {
        '\u2013': '-', '\u2014': '-', '\u2019': "'", '\u2018': "'",
        '\u201c': '"', '\u201d': '"'
    }
    for bad, good in replacements.items():
        text = text.replace(bad, good)
    return unicodedata.normalize('NFKD', text).encode('latin-1', 'ignore').decode('latin-1')

def extract_patient_name(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            first_line = f.readline()
            if first_line.lower().startswith("#patient"):
                return first_line.split(" ", 1)[1].strip().title()
        return "Nom Inconnu"
    except Exception as e:
        print(f"Erreur lors de l'extraction du nom : {e}")
        return "Nom Inconnu"

def format_date(date_str):
    try:
        date_str = str(int(float(date_str))).zfill(8)
        return f"{date_str[0:2]}/{date_str[2:4]}/{date_str[4:]}"
    except:
        return str(date_str)

def format_time(time_str):
    try:
        time_str = str(int(float(time_str))).zfill(6)
        return f"{time_str[0:2]}:{time_str[2:4]}:{time_str[4:]}"
    except:
        return str(time_str)

def add_generation_datetime(pdf, timestamp_str):
    pdf.set_font("Arial", 'I', 10)
    pdf.set_xy(150, 10)
    pdf.cell(0, 10, timestamp_str, ln=0, align='R')

variable_labels = {
    "AGE": "Âge",
    "HEIGHT": "Taille (cm)",
    "SBP": "Tension artérielle systolique (SBP)",
    "DBP": "Tension artérielle diastolique (DBP)",
    "FTPTT": "Temps de transit pied-doigt (FTPTT)",
    "FTPTT_CV": "Variabilité du temps de transit (FTPTT_CV)",
    "FTPWV": "Vitesse de l’onde de pouls pied-doigt (FTPWV)",
    "FTPWV_CV": "Variabilité de la vitesse d’onde de pouls (FTPWV_CV)",
    "HEART_RATE": "Fréquence cardiaque (bpm)",
    "HEART_RATE_CV": "Variabilité de la fréquence cardiaque (CV)",
    "FINGER_SIGNAL_AMP": "Amplitude du signal doigt",
    "TOE_SIGNAL_AMP": "Amplitude du signal orteil",
    "VALID_PULSES_PAIRS_NBR": "Nombre de paires de pouls valides",
    "SI": "Indice de rigidité (SI)",
    "CSP": "Pression systolique centrale (CSP)",
    "CDP": "Pression diastolique centrale (CDP)",
    "PSP": "Pression systolique périphérique (PSP)",
    "PDP": "Pression diastolique périphérique (PDP)",
    "TMS_FINGER_AOMI": "Temps moyen systolique doigt (TMS_FINGER_AOMI)",
    "TMS_TOE_AOMI": "Temps moyen systolique orteil (TMS_TOE_AOMI)",
    "IPS": "Indice de pulsation (IPS)",
    "SR": "Fréquence d’échantillonnage (SR)",
    "DATE": "Date",
    "TIME": "Heure"
}

def analyze_csv_and_generate_pdf(patient_csv_path, population_csv_path):
    patient_name = extract_patient_name(patient_csv_path)

    df = pd.read_csv(population_csv_path, encoding='utf-8-sig')
    df.columns = df.columns.str.strip().str.upper()
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    df = df.drop(columns=[c for c in ['LATERALITY', 'DATE', 'TIME', 'DEVICE', 'PATIENT'] if c in df.columns])
    stats = df.describe().transpose()

    with open(patient_csv_path, encoding='utf-8') as f:
        lines = f.readlines()

    individual_data = {}
    import re
    for line in lines:
        if line.startswith("#"):
            try:
                content = line.strip("#\n").strip()
                match = re.match(r"(.+?)\s+([\d\.,]+)$", content)
                if match:
                    raw_key = match.group(1).strip()
                    value = match.group(2).replace(",", ".")
                    key = re.sub(r"[^\w]+", "_", raw_key.upper()).strip("_")
                    individual_data[key] = value
            except Exception as e:
                print(f"Erreur parsing ligne : {line} - {e}")

    individual = pd.Series(individual_data)
    individual.index = individual.index.str.strip().str.upper()
    for col in individual.index:
        try:
            individual[col] = float(individual[col])
        except:
            individual[col] = individual[col]

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    timestamp_str = datetime.now().strftime("PDF généré : %d/%m/%Y à %H:%M")
    add_generation_datetime(pdf, timestamp_str)

    logo_path = os.path.join(os.path.dirname(__file__), 'static', 'img', 'logo.png')
    if os.path.isfile(logo_path):
        pdf.image(logo_path, x=10, y=8, w=75)

    pdf.set_xy(0, 40)
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(w=210, h=10, txt=clean_text(f"Rapport d'analyse – {patient_name}"), border=0, ln=1, align='C')
    pdf.ln(10)

    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "Données du patient :", ln=True)
    pdf.set_font("Arial", '', 12)
    for key, value in individual.items():
        if pd.notna(value):
            label = variable_labels.get(key, key)
            if key == "DATE":
                value = format_date(value)
            elif key == "TIME":
                value = format_time(value)
            pdf.cell(0, 8, clean_text(f"{label} : {value}"), ln=True)
    pdf.ln(10)

    temp_dir = tempfile.mkdtemp()

    for col in df.columns:
        if col in individual and pd.notna(individual[col]) and col in stats.index:
            try:
                val_float = float(individual[col])
            except:
                continue

            mean = stats.loc[col, "mean"]
            std = stats.loc[col, "std"]
            if pd.isna(mean) or pd.isna(std):
                continue
            z = (val_float - mean) / std if std != 0 else 0

            label = variable_labels.get(col, col)
            img_path = os.path.join(temp_dir, f"{col}.png")

            plt.figure(figsize=(6, 3))
            sns.histplot(df[col].dropna(), bins=25, color='skyblue', kde=False)
            plt.axvline(val_float, color='red', linestyle='--', label=f'Patient ({val_float:.2f})')
            plt.title(f"Histogramme de {label}")
            plt.xlabel(label)
            plt.ylabel("Fréquence")
            plt.legend()
            plt.tight_layout()
            plt.savefig(img_path, dpi=100)
            plt.close()

            pdf.add_page()
            pdf.set_font("Arial", 'B', 14)
            pdf.cell(0, 10, clean_text(label), ln=True)
            pdf.set_font("Arial", '', 12)
            pdf.cell(0, 8, clean_text(f"Valeur patient : {val_float:.2f}"), ln=True)
            pdf.cell(0, 8, clean_text(f"Moyenne population : {mean:.2f}"), ln=True)
            pdf.cell(0, 8, clean_text(f"Écart-type : {std:.2f}"), ln=True)
            pdf.cell(0, 8, clean_text(f"Z-score : {z:.2f}"), ln=True)
            pdf.ln(4)

            explication = (
                "Définition de l’écart type :\n"
                "L’écart type sert à mesurer si les données sont regroupées ou dispersées autour de la moyenne.\n\n"
                "Définition du Z-score :\n"
                "Le z-score indique à quel point une valeur est éloignée de la moyenne, en nombre d’écarts types."
            )
            pdf.set_font("Arial", 'I', 10)
            pdf.multi_cell(0, 6, clean_text(explication))
            pdf.ln(5)

            try:
                pdf.image(img_path, x=15, y=pdf.get_y(), w=180, h=90)
            except:
                continue

    for f in os.listdir(temp_dir):
        os.remove(os.path.join(temp_dir, f))
    os.rmdir(temp_dir)

    pdf_filename = f"rapport_{slugify(patient_name)}.pdf"
    output_pdf_path = os.path.join(PDF_OUTPUT_DIR, pdf_filename)
    pdf.output(output_pdf_path)

    print(f"Rapport généré dans : {output_pdf_path}")
    return patient_name, output_pdf_path
