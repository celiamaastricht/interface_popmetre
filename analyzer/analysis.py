import pandas as pd
import numpy as np
import os
import seaborn as sns
import matplotlib.pyplot as plt
from fpdf import FPDF
import tempfile
import matplotlib
matplotlib.use('Agg')  # Backend non interactif, sans GUI
import matplotlib.pyplot as plt

def analyze_csv_and_generate_pdf(patient_csv_path, population_csv_path, output_pdf_path):
    # Chargement population
    df = pd.read_csv(population_csv_path, encoding='utf-8-sig')

    # Conversion colonnes numériques
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # Colonnes à exclure
    colonnes_a_exclure = ['Laterality', 'Date', 'Time', 'Device', 'Patient']
    df = df.drop(columns=[col for col in colonnes_a_exclure if col in df.columns])

    # Stats globales population
    stats = df.describe().transpose()

    # Lecture patient
    with open(patient_csv_path, encoding='utf-8') as f:
        lines = f.readlines()

    # Extraction métadonnées patient
    individual_data = {}
    for line in lines:
        if line.startswith("#"):
            try:
                key, value = line.strip("#\n").split(maxsplit=1)
                individual_data[key] = value.replace(",", ".")
            except ValueError:
                continue
        else:
            break

    individual = pd.Series(individual_data)
    for col in individual.index:
        try:
            individual[col] = float(individual[col])
        except:
            individual[col] = np.nan

    # Initialiser PDF
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "Rapport d'analyse patient vs population", ln=True, align='C')
    pdf.ln(10)

    # Dossier temporaire pour images
    temp_dir = tempfile.mkdtemp()

    for col in df.columns:
        if col in individual and pd.notna(individual[col]) and col in stats.index:
            val = individual[col]
            mean = stats.loc[col, "mean"]
            std = stats.loc[col, "std"]
            z = (val - mean) / std if std != 0 else 0

            # Écrire stats dans PDF
            pdf.set_font("Arial", 'B', 14)
            pdf.cell(0, 10, f"--- {col} ---", ln=True)
            pdf.set_font("Arial", '', 12)
            pdf.cell(0, 8, f"Valeur individu : {val:.2f}", ln=True)
            pdf.cell(0, 8, f"Moyenne population : {mean:.2f}", ln=True)
            pdf.cell(0, 8, f"Écart-type population : {std:.2f}", ln=True)
            pdf.cell(0, 8, f"Z-score : {z:.2f}", ln=True)
            pdf.ln(4)

            # Générer histogramme
            plt.figure(figsize=(6, 3))
            sns.histplot(df[col].dropna(), kde=True, color='skyblue', bins=25)
            plt.axvline(val, color='red', linestyle='--', label=f'Individu ({val:.2f})')
            plt.title(f"{col} - Histogramme")
            plt.xlabel(col)
            plt.ylabel("Fréquence")
            plt.legend()
            plt.tight_layout()

            # Sauvegarder image temporaire
            img_path = os.path.join(temp_dir, f"{col}.png")
            plt.savefig(img_path)
            plt.close()

            # Ajouter image au PDF (largeur max 180)
            pdf.image(img_path, w=180)
            pdf.ln(10)

    # Sauvegarder PDF final
    pdf.output(output_pdf_path)

    # Nettoyer images temporaires
    for f in os.listdir(temp_dir):
        os.remove(os.path.join(temp_dir, f))
    os.rmdir(temp_dir)

    print(f"Rapport généré dans : {output_pdf_path}")
