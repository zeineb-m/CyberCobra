import os
from pathlib import Path

# -----------------------------

# Base directory

# -----------------------------

BASE_DIR = Path(**file**).resolve().parent.parent

# -----------------------------

# Security

# -----------------------------

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "dev-secret-key")
DEBUG = os.environ.get("DJANGO_DEBUG", "True") == "True"

# -----------------------------

# Allowed hosts

# -----------------------------

ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", "").split(",")
if not ALLOWED_HOSTS or ALLOWED_HOSTS == [""]:
ALLOWED_HOSTS = [
"localhost",
"127.0.0.1",
"cybercobra-4.onrender.com",  # backend Render
]

# -----------------------------

# Installed apps

# -----------------------------

INSTALLED_APPS = [
'django.contrib.admin',
'django.contrib.auth',
'django.contrib.contenttypes',
'django.contrib.sessions',
'django.contrib.messages',
'django.contrib.staticfiles',
'rest_framework',
'rest_framework_simplejwt',
'rest_framework_simplejwt.token_blacklist',
'corsheaders',
'auth_app',
'report',
'gestion_dequipement',
'gestion_camera',
'zones_app',
]

# -----------------------------

# Middleware

# -----------------------------

MIDDLEWARE = [
'django.middleware.security.SecurityMiddleware',
'corsheaders.middleware.CorsMiddleware',
'django.contrib.sessions.middleware.SessionMiddleware',
'django.middleware.common.CommonMiddleware',
'django.middleware.csrf.CsrfViewMiddleware',
'django.contrib.auth.middleware.AuthenticationMiddleware',
'django.contrib.messages.middleware.MessageMiddleware',
'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# -----------------------------

# Templates

# -----------------------------

TEMPLATES = [
{
"BACKEND": "django.template.backends.django.DjangoTemplates",
"DIRS": [BASE_DIR / "templates"],
"APP_DIRS": True,
"OPTIONS": {
"context_processors": [
"django.template.context_processors.debug",
"django.template.context_processors.request",
"django.contrib.auth.context_processors.auth",
"django.contrib.messages.context_processors.messages",
],
},
},
]

# -----------------------------

# URLs & WSGI

# -----------------------------

ROOT_URLCONF = 'CyberCobra.urls'
WSGI_APPLICATION = 'CyberCobra.wsgi.application'

# -----------------------------

# Database (FreeSQLDatabase)

# -----------------------------

DATABASES = {
"default": {
"ENGINE": "django.db.backends.mysql",
"NAME": "sql7805541",
"USER": "sql7805541",
"PASSWORD": "3uFlGmh3xY",
"HOST": "sql7.freesqldatabase.com",
"PORT": "3306",
"OPTIONS": {
"init_command": "SET sql_mode='STRICT_TRANS_TABLES'"
},
}
}

# -----------------------------

# Password validation

# -----------------------------

AUTH_PASSWORD_VALIDATORS = [
{"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
{"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
{"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
{"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# -----------------------------

# Internationalization

# -----------------------------

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# -----------------------------

# Static & media files

# -----------------------------

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / "media"

# -----------------------------

# CORS

# -----------------------------

CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = [
"[https://cybercobra-2.onrender.com](https://cybercobra-2.onrender.com)",             # Frontend Render
"http://localhost:3000",                         # Front local
"[https://v0-cyber-cobramain-three.vercel.app](https://v0-cyber-cobramain-three.vercel.app)",   # Front Vercel
]

# -----------------------------

# REST framework (JWT)

# -----------------------------

REST_FRAMEWORK = {
'DEFAULT_AUTHENTICATION_CLASSES': (
'rest_framework_simplejwt.authentication.JWTAuthentication',
),
}

# -----------------------------

# Optional: disable heavy libs on Render

# -----------------------------

# try:

# import face_recognition

# except ImportError:

# face_recognition = None
