from django.urls import path
from . import views
from .views import UploadAndAnalyzeCSV



urlpatterns = [
    path('', views.home_view, name='home'),
    path('login/', views.login_view, name='login'),
    path('upload_csv/', views.upload_csv_view, name='upload_csv'),
    path('api/analyze/', views.CSVAnalyzeAPIView.as_view(), name='api_analyze'),
     path('upload_and_analyze/', UploadAndAnalyzeCSV.as_view(), name='upload_and_analyze'),



]