from datatypes import Error
from exceptions import ConnectionError, RequestError, InvalidTypeOfResponseError
from typing import Callable
from json import JSONDecodeError
from time import sleep
import concurrent.futures
import requests
import warnings


def is_connected(function: Callable) -> Callable:

	def inner(*args, **kwargs):
		try:
			requests.head("https://google.com")
			return function(*args, **kwargs)

		except requests.ConnectionError as error:
			raise ConnectionError(
				message=f"Error! No connection to the Internet!",
				source=f"httprequests.is_connected, {error.__cause__}"
			)

	return inner


def catch_connection_errors(function):
	def inner(*args, **kwargs):
		try:
			return function(*args, **kwargs)

		except RequestError as error:
			warnings.warn(error)
			return Error(
				error_msg=error.message,
				error_type=error.error_type,
				error_source=error.source
			)

		except ConnectionError as error:
			return Error(
				error_msg=error.message,
				error_source=error.source,
				error_type=error.error_type
			)

	return inner


class Connections:

	@staticmethod
	@catch_connection_errors
	def safe_download(api_link: str):
		return Connections.download([api_link])

	@staticmethod
	def __load(url, timeout: int, text=False, status=False, delay=0.0):
		response_from_server = requests.get(url, timeout=timeout)

		if not response_from_server.ok:
			raise RequestError(
				message=f"Error! Status code is not 200 [OK], request failed!",
				source=f"httprequests.Connections.__load\nStatus code: {response_from_server.status_code}."
			)

		if delay > 0.0:
			sleep(delay)

		if status:
			return response_from_server.status_code

		if text:
			return response_from_server.text

		try:
			return response_from_server.json()

		except JSONDecodeError as exc:
			raise InvalidTypeOfResponseError(
				message=f"[Error] Cannot decode json.",
				source=f"Connections.__load, data_given = {response_from_server},"
				f"description = {exc.__cause__}"
			)

	@staticmethod
	@is_connected
	def download(urls, conns=100, text=False, status=False, timeout=5, delay=0.0) -> list:
		correct_output: list = list()
		with concurrent.futures.ThreadPoolExecutor(max_workers=conns) as executor:
			executor_to_url = (executor.submit(Connections.__load, url, timeout, text, status, delay) for url in urls)
			for future in concurrent.futures.as_completed(executor_to_url):
				try:
					outcome = future.result()
					correct_output.append(outcome)

				except Exception as exception:
					raise ConnectionError(
						message=f"Error: {exception}",
						source=exception.__cause__
					)

		return correct_output
