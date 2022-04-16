import json
import httpx

import api

from waiting import wait

from bear import Bear
from service import Service


SERVICE_TIMEOUT = 3  # seconds


class Client:
    __slots__ = ("service", "session")

    def __init__(self, service: Service):
        self.service = service
        self.session = httpx.Client(base_url=self.service.base_url)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()

    def get_info(self):
        return api.get_info(self.session)

    def get_bear(self, bear: Bear):
        return api.get_bear(self.session, b_id=bear.bear_id)

    def get_bears(self):
        return api.get_bears(self.session)

    def post_bear(self, bear: Bear, wait_result: bool = False) -> httpx.Response:
        if bear.bear_id:
            raise RuntimeError(f"bear is already has been registered: {bear}")

        res = api.post_bear(self.session,
                            bear_type=bear.bear_type, bear_name=bear.bear_name, bear_age=bear.bear_age)

        if res.status_code == 200:
            bear.set_id(bear_id=int(res.text))

            if wait_result:
                wait(lambda: self.check_registered(bear=bear),
                     timeout_seconds=SERVICE_TIMEOUT,
                     waiting_for=f"bear with id {bear.bear_id} to be registered " +
                                 f"response status: {res.status_code}, text: {res.text}")

        return res

    def put_bear(self, bear: Bear, wait_result: bool = False) -> httpx.Response:
        res = api.put_bear(self.session, b_id=bear.bear_id, b_type=bear.type, b_name=bear.name, b_age=bear.age)

        if res.status_code == 200:
            if wait_result:
                wait(lambda: self.check_registered(bear=bear),
                     timeout_seconds=SERVICE_TIMEOUT,
                     waiting_for=f"bear with id {bear.bear_id} to be updated\n" +
                                 f"response status: {res.status_code}, text: {res.text}")

        return res

    def delete_bear(self, bear: Bear, wait_result: bool = False) -> httpx.Response:
        res = api.delete_bear(self.session, b_id=bear.bear_id)

        if res.status_code == 200:
            if wait_result:
                wait(lambda: self.check_deleted(bear=bear),
                     timeout_seconds=SERVICE_TIMEOUT,
                     waiting_for=f"bear with id {bear.bear_id} to be deleted\n" +
                                 f"response status: {res.status_code}, text: {res.text}")

        return res

    def delete_bears(self, wait_result: bool = False) -> httpx.Response:
        res = api.delete_bears(self.session)

        if res.status_code == 200:
            if wait_result:
                wait(lambda: self.check_deleted_all(),
                     timeout_seconds=SERVICE_TIMEOUT,
                     waiting_for=f"all bears to be deleted\n" +
                                 f"response status: {res.status_code}, text: {res.text}")

        return res

    def check_registered(self, bear: Bear) -> bool:
        res = self.get_bear(bear=bear)
        if res.status_code == 200:
            return res.json() == json.loads(bear.to_json())
        return False

    def check_deleted(self, bear: Bear) -> bool:
        res = self.get_bear(bear=bear)
        if res.status_code == 200:
            return res.text == "EMPTY"
        return False

    def check_deleted_all(self) -> bool:
        res = self.get_bears()
        if res.status_code == 200:
            return res.json() == []
        return False
