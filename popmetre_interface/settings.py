import os
from pathlib import Path
from dotenv import load_dotenv

# Charge les variables d'environnement du fichier .env
load_dotenv()

# Base directory du projet
BASE_DIR = Path(__file__).resolve().parent.parent

# Clé secrète Django (doit être définie dans le fichier .env)
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY")
if not SECRET_KEY:
    raise Exception("La variable d'environnement DJANGO_SECRET_KEY n'est pas définie.")

# Mode debug
DEBUG = os.environ.get("DEBUG", "False").lower() in ("true", "1", "yes")

# Liste des hôtes autorisés
ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", "127.0.0.1").split(",")

# Applications installées
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rest_framework',
    'analyzer',
    'django_extensions',
]

# Middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Configuration des URLs
ROOT_URLCONF = 'popmetre_interface.urls'

# Configuration des templates
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# Point d'entrée WSGI
WSGI_APPLICATION = 'popmetre_interface.wsgi.application'

# Base de données (utilise PostgreSQL via .env)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.' + os.environ.get('DATABASE_ENGINE', 'sqlite3'),
        'NAME': os.environ.get('DATABASE_NAME', BASE_DIR / 'db.sqlite3'),
        'USER': os.environ.get('DATABASE_USERNAME', ''),
        'PASSWORD': os.environ.get('DATABASE_PASSWORD', ''),
        'HOST': os.environ.get('DATABASE_HOST', '127.0.0.1'),
        'PORT': os.environ.get('DATABASE_PORT', '5432'),
    }
}

# Validation des mots de passe
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalisation
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Fichiers statiques
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'analyzer' / 'static',
]


STATIC_ROOT = BASE_DIR / 'staticfiles'

# Clé primaire par défaut
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]
