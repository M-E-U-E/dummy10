import os

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://ollama:11434")
ALLOWED_HOSTS = ['127.0.0.1', 'localhost', 'django_app']  # Add your container name or domain

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('POSTGRES_DB', 'hotel_db'),
        'USER': os.getenv('POSTGRES_USER', 'username'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD', 'password'),
        'HOST': os.getenv('POSTGRES_HOST', 'db'),
        'PORT': os.getenv('POSTGRES_PORT', 5432),
    }
}
