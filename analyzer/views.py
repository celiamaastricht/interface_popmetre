from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from django.http import FileResponse, HttpResponseRedirect
import tempfile
import pandas as pd
import os
from .forms import AnalysisForm
from .analysis import analyze_csv_and_generate_pdf

# Page d'accueil simple
def home_view(request):
    return render(request, 'analyzer/home.html')

# Vue login
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('upload_csv')
        else:
            return render(request, 'analyzer/login.html', {'error': 'Identifiants invalides'})
    return render(request, 'analyzer/login.html')

# Upload CSV (page accessible uniquement aux utilisateurs connectés)
@login_required
def upload_csv_view(request):
    return render(request, 'analyzer/upload_csv.html')

# API REST qui analyse un CSV envoyé et renvoie un résumé JSON (simple)
class CSVAnalyzeAPIView(APIView):
    def post(self, request):
        csv_file = request.FILES.get('file')
        if not csv_file:
            return Response({"error": "Fichier CSV manquant"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            df = pd.read_csv(csv_file)
            analysis = df.describe().to_dict()
            return Response({"analysis": analysis}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# API REST qui reçoit un CSV population + un fichier patient, génère un PDF et le renvoie
class UploadAndAnalyzeCSV(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, format=None):
        print("Request FILES:", request.FILES)  # debug
        file_obj = request.FILES.get('file')
        if not file_obj:
            print("No file provided in request.")  # debug
            return Response({"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST)

        # Sauvegarder temporairement le fichier uploadé (patient CSV)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as temp_csv:
            for chunk in file_obj.chunks():
                temp_csv.write(chunk)
            temp_csv_path = temp_csv.name

        # Chemin fixe vers population CSV
        population_csv_path = r"C:\Users\celia\OneDrive\Documents\Axelife\Projet\metadata_all_patients.csv"

        # Créer un fichier PDF temporaire
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
            temp_pdf_path = temp_pdf.name

        # Appeler la fonction avec les 3 chemins attendus
        analyze_csv_and_generate_pdf(temp_csv_path, population_csv_path, temp_pdf_path)

        # Retourner le PDF en réponse (en tant que téléchargement)
        response = FileResponse(open(temp_pdf_path, 'rb'), content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="analysis_report.pdf"'

        return response

# Vue classique pour analyse avec formulaire
def analyze_view(request):
    if request.method == 'POST':
        patient_file = request.FILES.get('patient_file')

        if not patient_file:
            return render(request, 'analyzer/upload_csv.html', {'error': 'Veuillez fournir un fichier patient'})

        # Chemin fixe vers population CSV
        population_csv_path = r"C:\Users\celia\OneDrive\Documents\Axelife\Projet\metadata_all_patients.csv"

        # Sauvegarder temporairement le fichier patient uploadé
        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp_patient:
            for chunk in patient_file.chunks():
                tmp_patient.write(chunk)
            tmp_patient_path = tmp_patient.name

        # Créer un fichier PDF temporaire
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
            tmp_pdf_path = tmp_pdf.name

        # Générer PDF
        analyze_csv_and_generate_pdf(tmp_patient_path, population_csv_path, tmp_pdf_path)

        # Retourner PDF au client
        return FileResponse(open(tmp_pdf_path, 'rb'), as_attachment=True, filename="rapport.pdf")

    return render(request, 'analyzer/upload_csv.html')

# Vue avec formulaire pour plusieurs fichiers (exemple avancé)
def your_view(request):
    if request.method == 'POST':
        form = AnalysisForm(request.POST, request.FILES)
        if form.is_valid():
            files = request.FILES.getlist('files')  # Récupérer tous les fichiers uploadés

            pdf_paths = []
            for uploaded_file in files:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp_csv:
                    for chunk in uploaded_file.chunks():
                        tmp_csv.write(chunk)
                    tmp_csv_path = tmp_csv.name

                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
                    tmp_pdf_path = tmp_pdf.name

                # Ici tu peux adapter selon ta logique (exemple basique sans patient file)
                df_population = pd.read_csv(tmp_csv_path)

                # À modifier si nécessaire selon analyse
                # analyze_csv_and_generate_pdf(df_population, tmp_pdf_path)  # si modifié pour 2 arguments

                # Ici on simule appel fonction (à adapter)
                # pdf_paths.append(tmp_pdf_path)

            if pdf_paths:
                return FileResponse(open(pdf_paths[0], 'rb'), as_attachment=True, filename="rapport.pdf")

            return HttpResponseRedirect('/success/')
    else:
        form = AnalysisForm()

    return render(request, 'analyzer/upload_csv.html', {'form': form})