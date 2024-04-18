from google.cloud.bigquery import Row

from bq.connection import client


def run_query(query: str) -> list[dict]:
	"""
	Runs a query on BigQuery and returns the results.
	"""
	print(f"Running query: {query}")
	query_job = client.query(query)
	result = query_job.result()
	if not result:
		return []

	row: Row
	return [dict(row) for row in result]


def get_events(code: int, limit: int = 100, **where: str | int | float | bool) -> list[dict]:
	query = f"""
		SELECT *
		FROM `gdelt-bq.gdeltv2.events`
		WHERE EventRootCode='{code}'
		{'AND '.join([f"AND {key}={repr(value)}" for key, value in where.items()]) if where else ''}
		ORDER BY SqlDate
		LIMIT {limit};
		"""
	return run_query(query)


def get_most_fucked_countries(year: int, count: int = 5) -> list[dict]:
    query = f"""
        SELECT Actor1CountryCode, COUNT(*) as NumberOfEvents
        FROM `gdelt-bq.gdeltv2.events`
        WHERE EventRootCode='19' AND year={year} AND Actor1CountryCode!='None'
        GROUP BY Actor1CountryCode
        ORDER BY NumberOfEvents DESC
        LIMIT {count};
        """
    return run_query(query)
