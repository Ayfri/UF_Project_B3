import pandas as pd
import re
import textwrap

from google.cloud.bigquery import Row
from pandas import DataFrame

from bq.caching import get_request, has_request, save_request
from bq.connection import client


def run_query(query: str, debug: bool = True) -> DataFrame:
	"""
	Runs a query on BigQuery and returns the results.
	"""
	query = textwrap.dedent(query).strip().replace('\n', ' ')
	print(f"Running query: {re.sub(r' +', ' ', query)}")
	if has_request(query):
		if debug:
			print('Request already cached, returning cached data.')
		return pd.DataFrame(get_request(query))

	query_job = client.query(query)
	result = query_job.result()
	print(f"Query complete, fetching data.")
	if not result:
		return DataFrame()

	row: Row
	# Fetch rows in batches
	# Convert to DataFrame for efficient processing
	df = result.to_dataframe(progress_bar_type='tqdm' if debug else None)

	save_request(query, df.to_dict(orient='records'))
	return df


def get_events(code: int, limit: int = 100, order: str = "SqlDate", **where: str | int | float | bool) -> DataFrame:
	query = f"""
		SELECT *
		FROM `gdelt-bq.gdeltv2.events`
		WHERE EventRootCode='{code}'
		{'AND '.join([f"AND {key}={repr(value)}" for key, value in where.items()]) if where else ''}
		ORDER BY {order}
		LIMIT {limit};
		"""
	return run_query(query)


def get_all_events(limit: int = 100, order: str = "SqlDate", **where: str | int | float | bool) -> DataFrame:
	query = f"""
		SELECT *
		FROM `gdelt-bq.gdeltv2.events`
		{f'WHERE {" AND ".join([f"{key}={repr(value)}" for key, value in where.items()])}' if where else ''}
		ORDER BY {order}
		LIMIT {limit};
		"""
	return run_query(query)


def get_most_fucked_countries(year: int, count: int = 5) -> DataFrame:
	query = f"""
        SELECT Actor1CountryCode, COUNT(*) as NumberOfEvents
        FROM `gdelt-bq.gdeltv2.events`
        WHERE EventRootCode='19' AND year={year} AND Actor1CountryCode!='None'
        GROUP BY Actor1CountryCode
        ORDER BY NumberOfEvents DESC
        LIMIT {count};
    """
	return run_query(query)
