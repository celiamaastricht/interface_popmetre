from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.contrib import messages
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
import os
from django.conf import settings
from .analysis import analyze_csv_and_generate_pdf
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect

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
            if user.is_staff:
                return redirect('dashboard_admin')
            else:
                return redirect('upload_csv')
        else:
            messages.error(request, "Identifiants invalides")
            return render(request, 'analyzer/login.html')
    return render(request, 'analyzer/login.html')


# Page d’upload CSV (protégée)
@login_required
def upload_csv_view(request):
    return render(request, 'analyzer/upload_csv.html')


# Inscription utilisateur avec validation email + confirmation mdp + messages
def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        password2 = request.POST.get('password2', '')

        # Validation simple
        if not username or not email or not password or not password2:
            messages.error(request, "Tous les champs sont obligatoires.")
            return render(request, 'analyzer/register.html')

        if password != password2:
            messages.error(request, "Les mots de passe ne correspondent pas.")
            return render(request, 'analyzer/register.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Ce nom d'utilisateur est déjà pris.")
            return render(request, 'analyzer/register.html')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Cet email est déjà utilisé.")
            return render(request, 'analyzer/register.html')

        pattern = r'^(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()_+={}\[\]:;<>,.?/-]).{8,}$'
        if not re.match(pattern, password):
            messages.error(request, "Le mot de passe ne respecte pas les critères requis.")
            return render(request, 'analyzer/register.html')

        user = User.objects.create_user(username=username, email=email, password=password)
        messages.success(request, "Compte créé avec succès, vous pouvez maintenant vous connecter.")
        return redirect('login')

    return render(request, 'analyzer/register.html')
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages

# Liste utilisateurs (admin)
@staff_member_required
def user_list_view(request):
    if request.method == 'POST':
        delete_user_id = request.POST.get('delete_user_id')
        if delete_user_id:
            try:
                user_to_delete = User.objects.get(pk=delete_user_id)
                if request.user == user_to_delete:
                    messages.error(request, "Vous ne pouvez pas supprimer votre propre compte.")
                else:
                    user_to_delete.delete()
                    messages.success(request, f"L'utilisateur {user_to_delete.username} a été supprimé.")
            except User.DoesNotExist:
                messages.error(request, "Utilisateur introuvable.")
            return redirect('user_list')
        
        # Gestion des changements de rôle
        for key, value in request.POST.items():
            if key.startswith('role_'):
                try:
                    user_id = int(key.split('_')[1])
                    user = User.objects.get(id=user_id)
                    if user == request.user and value != 'admin':
                        messages.error(request, "Vous ne pouvez pas vous retirer du rôle admin.")
                        continue
                    user.is_staff = (value == 'admin')
                    user.save()
                except (ValueError, User.DoesNotExist):
                    continue
        messages.success(request, "Modifications enregistrées.")
        return redirect('user_list')

    users = User.objects.all()
    return render(request, 'analyzer/user_list.html', {'users': users})



@staff_member_required
def user_list_view(request):
    if request.method == 'POST':
        for key, value in request.POST.items():
            if key.startswith('role_'):
                try:
                    user_id = int(key.split('_')[1])
                    user = User.objects.get(id=user_id)

                    if user == request.user and value != 'admin':
                        messages.error(request, "Vous ne pouvez pas vous retirer du rôle admin.")
                        continue

                    new_is_staff = (value == 'admin')
                    if user.is_staff != new_is_staff:
                        user.is_staff = new_is_staff
                        user.save()
                        role = 'admin' if new_is_staff else 'user'
                        messages.success(request, f"L'utilisateur {user.username} a été mis {role}.")
                except (ValueError, User.DoesNotExist):
                    continue

        return redirect('user_list')

    users = User.objects.all()
    return render(request, 'analyzer/user_list.html', {'users': users})



# Toggle admin status (non utilisé si on fait par formulaire global)
@staff_member_required
def toggle_admin_view(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if user != request.user:
        user.is_staff = not user.is_staff
        user.save()
    return redirect('user_list')


# Décorateur admin personnalisé
def admin_required(view_func):
    return login_required(user_passes_test(lambda u: u.is_staff)(view_func))


# Dashboard admin
@login_required
def dashboard_admin_view(request):
    if not request.user.is_staff:
        return redirect('home')
    return render(request, 'analyzer/dashboard_admin.html')


# Suppression utilisateur avec confirmation
@login_required
@staff_member_required
def delete_user_view(request, user_id):
    user_to_delete = get_object_or_404(User, pk=user_id)

    if request.user == user_to_delete:
        messages.error(request, "Vous ne pouvez pas supprimer votre propre compte.")
        return redirect('user_list')

    if request.method == 'POST':
        user_to_delete.delete()
        messages.success(request, f"L'utilisateur {user_to_delete.username} a été supprimé.")
        return redirect('user_list')

    return redirect('user_list')


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

        population_csv_path = os.path.join(settings.BASE_DIR, 'data', 'metadata_all_patients.csv')

        patient_name, pdf_path = analyze_csv_and_generate_pdf(temp_csv_path, population_csv_path)

        safe_name = slugify_custom(patient_name) or "patient"
        pdf_filename = f"analysis_report_{safe_name}.pdf"

        response = FileResponse(
            open(pdf_path, 'rb'),
            content_type='application/pdf'
        )
        response['Content-Disposition'] = f'attachment; filename="{quote(pdf_filename)}"'
        response['X-Filename'] = quote(pdf_filename)
        return response
