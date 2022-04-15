import allure

from requests import Response
from httpx import Client


def get_info(client: Client) -> Response:
    url = "/info"
    with allure.step(f"GET {url}"):
        return client.get(url=url)


def get_bear(client: Client, b_id: int) -> Response:
    url = f"/bear/{b_id}"
    with allure.step(f"GET {url}"):
        return client.get(url=url)


def get_bears(client: Client) -> Response:
    url = "/bear"
    with allure.step(f"GET {url}"):
        return client.get(url=url)


def post_bear(client: Client, **kwargs) -> Response:
    url = "/bear"
    data = kwargs
    with allure.step(f"POST {url} payload: {data}"):
        return client.post(url=url, json=data)


def put_bear(client: Client, b_id: int, **kwargs) -> Response:
    url = f"/bear/{b_id}"
    data = kwargs
    with allure.step(f"POST {url} payload: {data}"):
        return client.put(url=url, json=data)


def delete_bear(client: Client, b_id: int) -> Response:
    url = f"/bear/:id={b_id}"
    with allure.step(f"DELETE {url}"):
        return client.delete(url=url)


def delete_bears(client: Client) -> Response:
    url = "/bear"
    with allure.step(f"DELETE {url}"):
        return client.delete(url=url)
