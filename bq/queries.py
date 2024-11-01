from functools import cache

import pandas as pd
import re
import textwrap

from google.cloud.bigquery import Row
from pandas import DataFrame

from bq.caching import get_request, has_request, save_request
from bq.connection import client


def create_wheres(*, add_where_keyword: bool = False, **where: str | int | float | bool | None) -> str:
    """
    Creates a WHERE clause from a dictionary.
    """
    if not where:
        return ''

    join = ' WHERE ' if add_where_keyword else ' AND '
    conditions = []
    for key, value in where.items():
        # Ensure the key is formatted properly with a valid operator
        match = re.match(r'^(.*?)([<>=!]+)$', key)
        if match:
            field, operator = match.groups()
            conditions.append(f"{field} {operator} {repr(value)}")
        else:
            conditions.append(f"{key}={repr(value)}")
    join += ' AND '.join(conditions)
    join = re.sub(r"='!=", "!='", join)
    join = re.sub(r"!='?None'?", " IS NOT NULL", join)
    join = re.sub(r"='?None'?", " IS NULL", join)
    return join


@cache
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
		{create_wheres(**where)}
		ORDER BY {order}
		LIMIT {limit};
		"""
	return run_query(query)


def get_all_events(limit: int = 100, order: str = "SqlDate", **where: str | int | float | bool) -> DataFrame:
	query = f"""
		SELECT *
		FROM `gdelt-bq.gdeltv2.events`
		{create_wheres(add_where_keyword=True, **where)}
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
