import os

from google.cloud import bigquery
from google.oauth2 import service_account

import dotenv
dotenv.load_dotenv()

credentials = service_account.Credentials.from_service_account_file(os.getenv("GOOGLE_APPLICATION_CREDENTIALS"))
client = bigquery.Client(credentials=credentials)
