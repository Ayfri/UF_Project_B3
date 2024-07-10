from bq.connection import redis_connection
import json


def get_request(request: str) -> list[dict]:
	"""
	Gets a request from the cache.
	"""
	return json.loads(redis_connection.get(request))


def has_request(request: str) -> bool:
	"""
	Checks if a request is in the cache.
	"""
	return redis_connection.exists(request)


def save_request(request: str, response: list[dict]) -> None:
	"""
	Stores a request and its response in the cache.
	"""
	redis_connection.set(request, json.dumps(response))
