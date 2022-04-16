import httpx as httpx

import api

from bear import Bear
from service import Service
from waiting import wait

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

    def post_bear(self, bear: Bear, wait_result: bool = False):
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

    def put_bear(self, bear: Bear, wait_result: bool = False):
        res = api.put_bear(self.session, b_id=bear.bear_id, b_type=bear.type, b_name=bear.name, b_age=bear.age)

        if res.status_code == 200:
            if wait_result:
                wait(lambda: self.check_registered(bear=bear),
                     timeout_seconds=SERVICE_TIMEOUT,
                     waiting_for=f"bear with id {bear.bear_id} to be updated\n" +
                                 f"response status: {res.status_code}, text: {res.text}")

        return res

    def delete_bear(self, bear: Bear, wait_result: bool = False):
        res = api.delete_bear(self.session, b_id=bear.bear_id)

        if res.status_code == 200:
            if wait_result:
                wait(lambda: self.check_deleted(bear=bear),
                     timeout_seconds=SERVICE_TIMEOUT,
                     waiting_for=f"bear with id {bear.bear_id} to be deleted\n" +
                                 f"response status: {res.status_code}, text: {res.text}")

        return res

    def delete_bears(self, wait_result: bool = False):
        res = api.delete_bears(self.session)

        if res.status_code == 200:
            if wait_result:
                wait(lambda: self.check_deleted_all(),
                     timeout_seconds=SERVICE_TIMEOUT,
                     waiting_for=f"all bears to be deleted\n" +
                                 f"response status: {res.status_code}, text: {res.text}")

        return res

    def check_registered(self, bear: Bear):
        res = self.get_bear(bear=bear)

        if res.status_code == 200:
            if res.json()["bear_name"] == bear.bear_name:
                if res.json()["bear_age"] == bear.bear_age:
                    if res.json()["bear_type"] == str(bear.bear_type):
                        return True

        return False

    def check_deleted(self, bear: Bear):
        return self.get_bear(bear=bear).text == "EMPTY"

    def check_deleted_all(self):
        return self.get_bears().json() == []

