# django_project/settings.py
from django.core.management.utils import get_random_secret_key
from pathlib import Path
import sys
import os
from dotenv import load_dotenv
import dj_database_url


load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", get_random_secret_key())

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv("DEBUG", "False") == "True"

DEVELOPMENT_MODE = os.getenv("DEVELOPMENT_MODE", "False") == "True"

if DEVELOPMENT_MODE:
    ALLOWED_HOSTS = ["*"]
else:
    ALLOWED_HOSTS = os.getenv(
        "DJANGO_ALLOWED_HOSTS", "127.0.0.1,localhost,0.0.0.0"
    ).split(",")


# Application definition

INSTALLED_APPS = [
    # 3rd party
    "django_user_agents",
    "django_bootstrap5",
    "django_extensions",
    "whitenoise.runserver_nostatic",
    "django.contrib.postgres",
    "rest_framework",
    "daphne",
    "channels",
    # default apps
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # my apps
    "accounts",
    "safesearch",
    "forum",
    "toto_api",
]

MIDDLEWARE = [
    "django_user_agents.middleware.UserAgentMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "accounts.middleware.ChildLastSeenMiddleware",
]

ROOT_URLCONF = "django_project.urls"

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
                "django_project.context_processors.set_section",
            ],
        },
    },
]


# WSGI_APPLICATION = "django_project.wsgi.application"
ASGI_APPLICATION = "django_project.asgi.application"

DEFAULT_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"

# Database settings
if DEVELOPMENT_MODE:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
        }
    }
elif len(sys.argv) > 0 and sys.argv[1] != "collectstatic":
    if os.getenv("DATABASE_URL", None) is None:
        raise Exception("DATABASE_URL environment variable not defined")
    DATABASES = {
        "default": dj_database_url.parse(os.environ.get("DATABASE_URL")),
    }


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_USER_MODEL = "accounts.User"


AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

LOGOUT_REDIRECT_URL = "login"
LOGIN_URL = "login"

# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "Africa/Nairobi"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = "static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]

# media files
MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# Google Search Settings
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
CUSTOM_SEARCH_ENGINE_ID = os.getenv("CUSTOM_SEARCH_ENGINE_ID")

# Email settings
EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
EMAIL_PORT = int(os.getenv("EMAIL_PORT"))
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS").lower() == "true"
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL")

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

LOGGING = {
    "version": 1,
    # The version number of our log
    "disable_existing_loggers": False,
    # django uses some of its own loggers for internal operations. In case you want to disable them just replace the False above with true.
    # A handler for WARNING. It is basically writing the WARNING messages into a file called WARNING.log
    "handlers": {
        "file": {
            "level": "WARNING",
            "class": "logging.FileHandler",
            "filename": BASE_DIR / "warning.log",
        },
    },
    # A logger for WARNING which has a handler called 'file'. A logger can have multiple handler
    "loggers": {
        # notice the blank '', Usually you would put built in loggers like django or root here based on your needs
        "": {
            "handlers": [
                "file"
            ],  # notice how file variable is called in handler which has been defined above
            "level": "WARNING",
            "propagate": True,
        },
    },
}

SESSION_EXPIRE_AT_BROWSER_CLOSE = True

CHANNEL_LAYERS = {
    "default": {"BACKEND": "channels.layers.InMemoryChannelLayer"},
}

CSRF_TRUSTED_ORIGINS = [
    "https://*.naftalmatoya.me",
    "http://localhost:8001",
    "http://127.0.0.1:8001",
    "http://0.0.0.0:8001",
]

SECURE_SSL_REDIRECT=False