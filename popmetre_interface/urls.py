from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from django.urls import re_path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('analyzer.urls')),  # redirige vers l'app analyzer
    path('analyzer/', include('analyzer.urls')),
]
import os
print("DEBUG =", settings.DEBUG)
print("STATIC_URL =", settings.STATIC_URL)
print("STATIC_ROOT =", settings.STATIC_ROOT)
print("staticfiles dir exists:", os.path.exists(settings.STATIC_ROOT))

if settings.DEBUG:
    urlpatterns += [
        re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),
    ]