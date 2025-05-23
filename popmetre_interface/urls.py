from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('analyzer.urls')),  # redirige vers l'app analyzer
    path('analyzer/', include('analyzer.urls')),
]