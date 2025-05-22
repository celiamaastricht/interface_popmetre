from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from django.http import FileResponse
from django.utils.text import slugify
from urllib.parse import quote
import tempfile
import pandas as pd
import re
from .analysis import analyze_csv_and_generate_pdf

# Page d'accueil
def home_view(request):
    return render(request, 'analyzer/home.html')

# Connexion utilisateur
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

# Page d’upload CSV (protégée)
@login_required
def upload_csv_view(request):
    return render(request, 'analyzer/upload_csv.html')

# API REST simple (analyse CSV → JSON)
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

# Utilitaire : slugify personnalisé
def slugify_custom(value):
    value = str(value).strip().lower()
    value = re.sub(r'[^a-z0-9]+', '-', value)
    return value.strip('-')

# API REST complète (CSV patient → PDF)
class UploadAndAnalyzeCSV(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, format=None):
        file_obj = request.FILES.get('file')
        if not file_obj:
            return Response({"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as temp_csv:
            for chunk in file_obj.chunks():
                temp_csv.write(chunk)
            temp_csv_path = temp_csv.name

        population_csv_path = r"C:\Users\celia\OneDrive\Documents\Axelife\Projet\metadata_all_patients.csv"

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
            temp_pdf_path = temp_pdf.name

        # Appelle l'analyse et récupère le nom du patient
        patient_name = analyze_csv_and_generate_pdf(temp_csv_path, population_csv_path, temp_pdf_path)
        safe_name = slugify_custom(patient_name) or "patient"

        pdf_filename = f"analysis_report_{safe_name}.pdf"

        response = FileResponse(
            open(temp_pdf_path, 'rb'),
            content_type='application/pdf'
        )
        response['Content-Disposition'] = f'attachment; filename="{quote(pdf_filename)}"'
        response['X-Filename'] = quote(pdf_filename)  # Pour JavaScript
        return response
