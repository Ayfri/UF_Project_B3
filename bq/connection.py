import os

import redis
from google.cloud import bigquery
from google.oauth2 import service_account

import dotenv
dotenv.load_dotenv()

credentials = service_account.Credentials.from_service_account_file(os.getenv("GOOGLE_APPLICATION_CREDENTIALS"))
client = bigquery.Client(credentials=credentials)

redis_connection = redis.Redis(host=os.getenv("REDIS_HOST"), port=os.getenv("REDIS_PORT"), password=os.getenv("REDIS_PASSWORD"))
