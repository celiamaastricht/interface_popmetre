from django.urls import path
from . import views
from .views import UploadAndAnalyzeCSV
from .views import home_view, login_view, upload_csv_view, register_view,user_list_view,toggle_admin_view, delete_user_view


urlpatterns = [
    path('', views.home_view, name='home'),
    path('login/', views.login_view, name='login'),
    path('upload_csv/', views.upload_csv_view, name='upload_csv'),
    path('api/analyze/', views.CSVAnalyzeAPIView.as_view(), name='api_analyze'),
    path('register/', register_view, name='register'),
    path('admin/users/', user_list_view, name='user_list'),
    path('upload_and_analyze/', UploadAndAnalyzeCSV.as_view(), name='upload_and_analyze'),
    path('admin/users/toggle_admin/<int:user_id>/', toggle_admin_view, name='toggle_admin'),
    path('dashboard-admin/', views.dashboard_admin_view, name='dashboard_admin'),
    path('utilisateurs/', views.user_list_view, name='user_list'),
    path('delete_user/<int:user_id>/', delete_user_view, name='delete_user'),


]