from google.cloud import bigquery
from pprint import pprint


def main() -> None:
    client = bigquery.Client()

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
