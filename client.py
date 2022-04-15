import httpx as httpx

import api

from bear import Bear
from service import Service


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

    def get_bear(self, bear_id: int):
        return api.get_bear(self.session, b_id=bear_id)

    def get_bears(self):
        return api.get_bears(self.session)

    def post_bear(self, bear: Bear):
        if bear.bear_id:
            raise RuntimeError(f"bear is already has been registered: {bear}")

        response = api.post_bear(self.session,
                                 bear_type=bear.bear_type, bear_name=bear.bear_name, bear_age=bear.bear_age)

        if response.status_code == 200:
            bear.set_id(bear_id=int(response.text))

            return response

    def put_bear(self, bear: Bear, bear_id: int = None):
        bear_id = bear_id or bear.id
        response = api.put_bear(self.session, b_id= bear_id, b_type=bear.type, b_name=bear.name, b_age=bear.age)

        return response

    def delete_bear(self, bear_id: int):
        return api.delete_bear(self.session, b_id=bear_id)

    def delete_bears(self):
        return api.delete_bears(self.session)
