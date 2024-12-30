import os

DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql+psycopg2://username:password@db:5432/hotel_db')
OLLAMA_URL = os.getenv('OLLAMA_URL', 'http://ollama:11434')


BOT_NAME = 'trip'
SPIDER_MODULES = ['trip.spiders']
NEWSPIDER_MODULE = 'trip.spiders'
