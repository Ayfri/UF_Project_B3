import os

import dotenv
from google.cloud import bigquery
from google.oauth2 import service_account
from pprint import pprint

dotenv.load_dotenv()

def main() -> None:
    credentials = service_account.Credentials.from_service_account_file(os.getenv("GOOGLE_APPLICATION_CREDENTIALS"))
    client = bigquery.Client(credentials=credentials)

    # Perform a query.
    QUERY = (
        """
        SELECT SqlDate, COUNT(*) as TotalEvents
        FROM `gdelt-bq.gdeltv2.events`
        WHERE EventRootCode='19'
        GROUP BY SqlDate
        ORDER BY SqlDate
        LIMIT 100;
        """
    )

    query_job = client.query(QUERY)  # API request
    rows = query_job.result()  # Waits for query to finish

    for row in rows:
        pprint(row)


if __name__ == "__main__":
    main()
