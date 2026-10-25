from pathlib import Path
from datetime import timedelta

from django.conf.global_settings import AUTH_USER_MODEL
from decouple import config
# =========================================================
# BASE
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent



# =========================================================
# SECURITY
# =========================================================

SECRET_KEY = config("SECRET_KEY")

DEBUG = config("DEBUG", cast=bool)

CSRF_TRUSTED_ORIGINS = config(
    "CSRF_TRUSTED_ORIGINS",
    cast=lambda v: [s.strip() for s in v.split(",") if s.strip()],
    default=""
)

ALLOWED_HOSTS = config(
    "ALLOWED_HOSTS",
    cast=lambda v: [s.strip() for s in v.split(",")],
    default="127.0.0.1",
)

# =========================================================
# APPLICATIONS
# =========================================================

DJANGO_APPS = [
    "jazzmin",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

THIRD_PARTY_APPS = [
    "rest_framework",
    "rest_framework_simplejwt", 
    # "django_filters",
    # 'corsheaders',
]

DEBUG_TOOLS = [
    # "silk",
    'drf_spectacular',
]

LOCAL_APPS = [
    'apps.users',
    'apps.authentication',
    'apps.common',
]
if DEBUG:
    INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS + DEBUG_TOOLS
else:  
    INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS





# =========================================================
# MIDDLEWARE
# =========================================================

MIDDLEWARE = [
    #  'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

WSGI_APPLICATION = 'edumate.wsgi.application'

if DEBUG:
    MIDDLEWARE += ["silk.middleware.SilkyMiddleware"]


# =========================================================
# TEMPLATES
# =========================================================

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

ROOT_URLCONF = 'edumate.urls'



# =========================================================
# DATABASE
# =========================================================

# DATABASES = {
#     'default': {
#         'ENGINE': config("ENGINE", default="django.db.backends.postgresql"),
#         'NAME': config("PGDATABASE", default=config("DB_NAME", default="")),
#         'USER': config("PGUSER", default=config("DB_USER", default="")),
#         'PASSWORD': config("PGPASSWORD", default=config("DB_PASSWORD", default="")),
#         'HOST': config("PGHOST", default=config("DB_HOST", default="127.0.0.1")),
#         'PORT': config("PGPORT", default=config("DB_PORT", default="5432")),
#     }
# }



# =========================================================
# AUTH PASSWORD VALIDATORS
# =========================================================

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {'min_length': 8}, # Можно изменить минимальную длину
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]



# =========================================================
# AUTH PASSWORD VALIDATORS
# =========================================================

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'  # Replace with your SMTP provider
EMAIL_PORT = 587
EMAIL_USE_TLS = True

# Authentication (Keep these secure using environment variables)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', 'your-email@gmail.com')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', 'your-app-password')

# Default From Email address
DEFAULT_FROM_EMAIL = f"Edumate <{EMAIL_HOST_USER}>"



# =========================================================
# INTERNATIONALIZATION
# =========================================================

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True



# =========================================================
# STATIC & MEDIA FILES
# =========================================================

STATIC_URL = "static/"

STATIC_ROOT = BASE_DIR / "static"


MEDIA_URL = "/media/"

MEDIA_ROOT = BASE_DIR / "media"



# # =========================================================
# # DJANGO DEFAULTS
# # =========================================================

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_USER_MODEL = "users.User"

# LOGIN_URL = "/auth/access-denied/"


# # =========================================================
# # DJANGO REST FRAMEWORK
# # =========================================================

REST_FRAMEWORK = {
   
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PARSER_CLASSES": [
        "rest_framework.parsers.JSONParser",
        "rest_framework.parsers.FormParser",
        "rest_framework.parsers.MultiPartParser",
    ],
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "10/min"
    }
}


# # =========================================================
# # SIMPLE JWT
# # =========================================================

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": config("ACCESS_TOKEN_LIFETIME", default=timedelta(minutes=100)),
    "REFRESH_TOKEN_LIFETIME": config("REFRESH_TOKEN_LIFETIME", default=timedelta(days=1)),
    "ROTATE_REFRESH_TOKENS": True,
}


# # =========================================================
# # DRF SPECTACULAR
# # =========================================================

SPECTACULAR_SETTINGS = {
    'TITLE': 'Freelance System API',
    'DESCRIPTION': 'Freelance APIs',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}


# # =========================================================
# # CORS
# # =========================================================

# CORS_ALLOWED_ORIGINS = [
#     "http://localhost:5173",
# ]