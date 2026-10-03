import os
from pathlib import Path
from decouple import config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/6.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config("SECRET_KEY", default="django-insecure-!@#4$%&*()_+1234567890qwertyuiopasdfghjklzxcvbnm")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config("DEBUG", cast=bool, default=False)

ALLOWED_HOSTS = [
    host.strip() for host in config("ALLOWED_HOSTS", default="").split(",")
    if host.strip()  # Remove espaços em branco e ignore entradas vazias
]



if not DEBUG:

    CSRF_TRUSTED_ORIGINS = [
        origin.strip() for origin in config("CSRF_TRUSTED_ORIGINS", default="").split(",")
        if origin.strip()  # Remove espaços em branco e ignore entradas vazias
    ]

    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

    # Força o redirecionamento permanente (301) de HTTP para HTTPS
    SECURE_SSL_REDIRECT = True  # Defina como True em produção

    # Isenta a rota /health/ do redirecionamento para HTTPS
    SECURE_REDIRECT_EXEMPT = [r'^health/$']

    # Protege o cookie de sessão contra envio em conexões não-seguradas
    SESSION_COOKIE_SECURE = True 

    # Protege o cookie do CSRF contra envio em conexões não-seguradas
    CSRF_COOKIE_SECURE = True 

    # Habilita o HSTS com duração de 1 ano (em segundos)
    SECURE_HSTS_SECONDS = 31536000  # 1 ano 

    # Inclui subdomínios na regra do HSTS (opcional, remova se usar subdomínios HTTP)
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True

    # Garante que o HSTS não seja removido acidentalmente
    SECURE_HSTS_PRELOAD = True  # Defina como True se você quiser enviar seu site para a lista de pré-carregamento HSTS


# Application definition

INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',
    'whitenoise',
    'django_ckeditor_5',
    'blog',
    'pwa',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, "templates"),],
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

WSGI_APPLICATION = 'core.wsgi.application'


AUTH_USER_MODEL = "blog.Author"


# Database
# https://docs.djangoproject.com/en/6.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config("POSTGRES_DB", default="postgres"),
        'USER': config("POSTGRES_USER", default="postgres"),
        'PASSWORD': config("POSTGRES_PASSWORD", default="postgres"),
        'HOST': config("POSTGRES_HOST", default="localhost"),
        'PORT': config("POSTGRES_PORT", default="5432", cast=int),
    }
}

# Redis Cache
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": "redis://localhost:6379/1",  # Use a porta padrão do Redis
    }
}

# Password validation
# https://docs.djangoproject.com/en/6.0/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/6.0/topics/i18n/

LANGUAGE_CODE = 'pt-BR'

TIME_ZONE = 'America/Sao_Paulo'

USE_I18N = True

USE_TZ = False


default_auto_field = 'django.db.models.BigAutoField'


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/6.0/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, "static"),]
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")


# Configuração customizada para o CKEditor 5
CKEDITOR_5_UPLOAD_FILE_VIEW_NAME = "ckeditor5_image_upload"

CKEDITOR_5_CONFIGS = {
    "default": {
        "toolbar": [
            "heading",
            "|",
            "bold",
            "italic",
            "link",
            "imageUpload",
            "|",
            "blockQuote",
            "insertTable",
            "mediaEmbed",
            "undo",
            "redo",
        ],
        "image": {
            "toolbar": [
                "imageTextAlternative",
                "|",
                "imageStyle:alignLeft",
                "imageStyle:alignCenter",
                "imageStyle:alignRight",
                "|",
                "resizeImage",
            ],
        },
    }
}

CKEDITOR5_CONFIGS = CKEDITOR_5_CONFIGS

# Configuração do envio de e-mails
EMAIL_BACKEND = config("EMAIL_BACKEND", default="django.core.mail.backends.smtp.EmailBackend")
EMAIL_HOST = config("EMAIL_HOST", default="localhost")
EMAIL_PORT = config("EMAIL_PORT", cast=int, default=587)
EMAIL_USE_TLS = config("EMAIL_USE_TLS", cast=bool, default=True)
EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default="")
DEFAULT_FROM_EMAIL = config("DEFAULT_FROM_EMAIL", default="webmaster@localhost")

PWA_APP_NAME = 'Toda Garota Blog'
PWA_APP_SHORT_NAME = 'Toda Garota'
PWA_APP_DESCRIPTION = "O seu espaço seguro de dicas, inspiração e tudo que envolve o universo feminino."
PWA_APP_THEME_COLOR = '#D38B8B'
PWA_APP_BACKGROUND_COLOR = '#FFF5F5'
PWA_APP_DISPLAY = 'standalone'
PWA_APP_SCOPE = '/'
PWA_APP_ORIENTATION = 'any'
PWA_APP_START_URL = '/'
PWA_APP_STATUS_BAR_COLOR = 'default'

PWA_APP_ICONS = [
    {
        "src": "/static/img/logo-48x48.png",
        "sizes": "48x48",
        "type": "image/png",
    },
    {
        "src": "/static/img/logo-72x72.png",
        "sizes": "72x72",
        "type": "image/png",
    },
    {
        "src": "/static/img/logo-96x96.png",
        "sizes": "96x96",
        "type": "image/png",
    },
    {
        "src": "/static/img/logo-144x144.png",
        "sizes": "144x144",
        "type": "image/png",
    },
    {
        "src": "/static/img/logo-192x192.png",
        "sizes": "192x192",
        "type": "image/png",
    },
    {
        "src": "/static/img/logo-512x512.png",
        "sizes": "512x512",
        "type": "image/png",
        "purpose": "any",
    },
    {
        "src": "/static/img/logo-512x512-maskable.png",
        "sizes": "512x512",
        "type": "image/png",
        "purpose": "maskable",
    },
]

PWA_APP_ICONS_APPLE = [
    {
        "src": "/static/img/logo-160x160.png",
        "sizes": "160x160",
        "type": "image/png"
    }
]

PWA_APP_SCREENSHOTS = [
    {
        "src": "/static/img/desktop.png",
        "sizes": "1920x911",
        "type": "image/png",
        "form_factor": "wide",
        "label": "Desktop View",
    },
    {
        "src": "/static/img/mobile.png",
        "sizes": "378x869",
        "type": "image/png",
        "form_factor": "narrow",
        "label": "Mobile View",
    },
]

PWA_APP_SHORTCUTS = [
    {
        'name': 'Toda Garota Blog',
        'short_name': 'Toda Garota',
        'description': 'O seu espaço seguro de dicas, inspiração e tudo que envolve o universo feminino.',
        'url': '/',
        "icons": [
            {
            "src": "/static/img/logo-96x96.png",
            "sizes": "96x96",
            "type": "image/png"
            }
        ]
    },
]

PWA_APP_LANG = 'pt-BR'
PWA_APP_CATEGORIES = ['lifestyle', 'beauty', 'health']  # Categorias oficiais aceitas
PWA_APP_DEBUG_MODE = False  # Desativa o modo de depuração para produção

JAZZMIN_SETTINGS = {
    "site_title": "GardenBrows Blog Admin",
    "site_header": "GardenBrows Blog",
    "site_brand": "GardenBrows Blog",
    # "site_logo": "/img/logo-96x96.png",
    "login_logo": None,
    "icons": {
        "auth": "fas fa-users-cog",
        "blog.author": "fas fa-user",
        "auth.Group": "fas fa-users",
        "blog.Post": "fas fa-newspaper",
        "blog.Category": "fas fa-layer-group",
        "blog.Tag": "fas fa-tags",
    },
    "user_avatar": "avatar_url",  # Função para obter o avatar do usuário
    "custom_css": "css/custom_admin.css",
    "welcome_sign": "Bem-vindo(a) ao GardenBrows Blog",
    "copyright": "GardenBrows Blog",
}