from http import HTTPStatus

import httpx
from retrying import retry
from waiting import wait

import docker_helper as docker_helper

START_TIMEOUT = 30  # seconds
STOP_TIMEOUT = 30  # seconds


class Service:
    __slots__ = ("image", "exposed_port", "container")

    def __init__(self, image, exposed_port):
        self.image = image
        self.exposed_port = exposed_port
        self.container = None

    def __enter__(self):
        self.container = docker_helper.run(image=self.image, exposed_port=self.exposed_port, timeout=START_TIMEOUT)
        self._wait_service()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.container.stop(timeout=STOP_TIMEOUT)
        self.container.remove()

    @property
    def id(self):
        if self.container:
            return self.container.id

    @property
    def pid(self):
        if self.container:
            return self.container.pid

    @property
    def logs(self):
        if self.container:
            self.container.reload()
            return self.container.logs()

    @property
    def log_file(self):
        return f"/var/lib/docker/containers/{self.id}/{self.id}-json.log"

    @property
    def base_url(self):
        if self.container:
            return docker_helper.get_service_url_base(container=self.container, exposed_port=self.exposed_port)

    def _wait_service(self):
        wait(retry(lambda: httpx.Client().get(f"{self.base_url}/info").status_code == 200),
             timeout_seconds=HTTPStatus.OK,
             waiting_for="service started")
