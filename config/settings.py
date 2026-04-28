from pathlib import Path
from decouple import config
from datetime import timedelta

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config("SECRET_KEY")
DEBUG = config("DEBUG", default=False, cast=bool)

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = config("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD")

PAYMOB_SECRET_KEY = config("PAYMOB_SECRET_KEY")
PAYMOB_PUBLIC_KEY = config("PAYMOB_PUBLIC_KEY", default="")
PAYMOB_HMAC_SECRET = config("PAYMOB_HMAC_SECRET")
PAYMOB_CARD_INTEGRATION_ID = config("PAYMOB_CARD_INTEGRATION_ID")
# PAYMOB_SUCCESS_URL = config(
#     "PAYMOB_SUCCESS_URL",
#     default="https://tcg-egypt.com/points/success",
# )
# PAYMOB_FAILURE_URL = config(
#     "PAYMOB_FAILURE_URL",
#     default="https://tcg-egypt.com/points/failed",
# )

PAYMOB_SUCCESS_URL = config(
    "PAYMOB_SUCCESS_URL",
    default="http://localhost:3000/profile",
)

PAYMOB_FAILURE_URL = config(
    "PAYMOB_FAILURE_URL",
    default="http://localhost:3000/profile",
)

EMAIL_TIMEOUT = 5  # seconds

DEFAULT_FROM_EMAIL = config(
    "DEFAULT_FROM_EMAIL",
    default=f"TCG Egypt <{EMAIL_HOST_USER}>"
)
SERVER_EMAIL = DEFAULT_FROM_EMAIL

FRONTEND_URL = config("FRONTEND_URL", default="http://localhost:3000")
PASSWORD_RESET_TIMEOUT = 60 * 60 * 2


LISTING_POINT_COST = config("LISTING_POINT_COST", default=20, cast=int)

ALLOWED_HOSTS = [
    "tcg-egypt.com",
    "www.tcg-egypt.com",
    "api.tcg-egypt.com",
    "127.0.0.1",
    "localhost",
    config("RENDER_EXTERNAL_HOSTNAME", default=""),
]

CSRF_TRUSTED_ORIGINS = [
    "https://tcg-egypt.com",
    "https://www.tcg-egypt.com",
    "https://api.tcg-egypt.com",
]

render_host = config("RENDER_EXTERNAL_HOSTNAME", default="")
if render_host:
    CSRF_TRUSTED_ORIGINS.append(f"https://{render_host}")

AUTH_USER_MODEL = "users.CustomUser"

INSTALLED_APPS = [
    "users.apps.UsersConfig",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    "corsheaders",
    "rest_framework",

    "cards",
    "cart",
    "orders",
    # "points",
    "content",
    "points.apps.PointsConfig",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config("DB_NAME"),
        "USER": config("DB_USER"),
        "PASSWORD": config("DB_PASSWORD"),
        "HOST": config("DB_HOST", default="localhost"),
        "PORT": config("DB_PORT", default="5432"),
    }
}

AUTH_PASSWORD_VALIDATORS = []

LANGUAGE_CODE = "en-us"
TIME_ZONE = "Africa/Cairo"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://192.168.1.3:3000",
    "https://tcg-egypt.com",
    "https://www.tcg-egypt.com",
]

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.AllowAny",
    ),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=30),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
}

if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_SSL_REDIRECT = True