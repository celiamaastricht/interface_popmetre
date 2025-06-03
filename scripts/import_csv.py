import os
import sys

# Ajoute le chemin racine du projet au PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'popmetre_interface.settings')

import django
django.setup()

import pandas as pd
from django.db import connection
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'popmetre_interface.settings')
django.setup()

def run():
    csv_path = '/app/data/metadata_all_patients.csv'
    df = pd.read_csv(csv_path, sep=',', encoding='utf-8')

    print("Colonnes CSV :", list(df.columns))

    def to_int(val):
        try:
            return int(val)
        except (ValueError, TypeError):
            return None

    def to_float(val):
        try:
            return float(val)
        except (ValueError, TypeError):
            return None

    with connection.cursor() as cursor:
        for i, (_, row) in enumerate(df.iterrows()):
            age = to_int(row['Age'])
            height = to_int(row['Height'])
            sbp = to_int(row['SBP'])
            dbp = to_int(row['DBP'])
            heart_rate = to_int(row['Heart_Rate'])
            valid_pulses_pairs_nbr = to_int(row['Valid_Pulses_Pairs_Nbr'])
            sr = to_int(row['SR'])

            # Vérifie si des valeurs int dépassent les bornes
            for val, name in [(age, 'Age'), (height, 'Height'), (sbp, 'SBP'), (dbp, 'DBP'), (heart_rate, 'Heart_Rate'), (valid_pulses_pairs_nbr, 'Valid_Pulses_Pairs_Nbr'), (sr, 'SR')]:
                if val is not None and (val > 2147483647 or val < -2147483648):
                    print(f"Value too big for integer: {name} = {val} at row {i}")

            values = (
                row['Patient'],
                age,
                height,
                row['Laterality'],
                row['Date'],
                row['Time'],
                sbp,
                dbp,
                to_float(row['FTPTT']),
                to_float(row['FTPTT_CV']),
                to_float(row['FTPWV']),
                to_float(row['FTPWV_CV']),
                heart_rate,
                to_float(row['Heart_Rate_CV']),
                to_float(row['Finger_Signal_Amp']),
                to_float(row['Toe_Signal_Amp']),
                valid_pulses_pairs_nbr,
                to_float(row['SI']),
                to_float(row['CSP']),
                to_float(row['CDP']),
                to_float(row['PSP']),
                to_float(row['PDP']),
                to_float(row['TMS_FINGER_AOMI']),
                to_float(row['TMS_TOE_AOMI']),
                to_float(row['IPS']),
                sr,
                row['Device']
            )

            if i < 5:
                print(values)

            cursor.execute("""
                INSERT INTO mesures (
                    patient, age, height, laterality, date, time, sbp, dbp, ftptt, ftptt_cv,
                    ftpwv, ftpwv_cv, heart_rate, heart_rate_cv, finger_signal_amp, toe_signal_amp,
                    valid_pulses_pairs_nbr, si, csp, cdp, psp, pdp, tms_finger_aomi, tms_toe_aomi,
                    ips, sr, device
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, values)
