import docker
import socket

from docker.errors import APIError
from docker.models.containers import Container
from enum import Enum
from requests import HTTPError
from waiting import wait

from common_helper import get_from_multilevel_dict


DOCKER_TIMEOUT = 120  # seconds

IMAGE = "azshoo/alaska"
CONTAINER_EXPOSED_PORT = 8091

CONTAINER_START_TIMEOUT = 120  # seconds
CONTAINER_STOP_TIMEOUT = 120  # seconds


class ContainerStatus(Enum):
    CREATED = "created"
    RESTARTING = "restarting"
    RUNNING = "running"
    REMOVING = "removing"
    PAUSED = "paused"
    EXITED = "exited"
    DEAD = "dead"

    def __str__(self):
        return self.value

    @staticmethod
    def get_by_value(value: str):
        for status in ContainerStatus:
            if status.value == value:
                return status

        raise ValueError(f"no such container status: {value}")


def get_docker_client():
    return docker.from_env()


def run(image: str, exposed_port: int, timeout: int) -> Container:
    client = get_docker_client()
    while True:
        binding_port = get_free_port()
        try:
            cntr = client.containers.run(image=image, ports={exposed_port: binding_port}, detach=True)
        except APIError as e:
            raise RuntimeError("can not start the service container") from e
        except HTTPError as e:
            if e.response.text.endswith("port is already allocated", 0, -3):
                continue
        else:
            wait_for_running_status(container=cntr, timeout=timeout)
            return cntr


def get_container_param(cntr: Container, param: str):
    cntr.reload()
    return get_from_multilevel_dict(multilevel_dict=cntr.attrs, key=param)


def get_container_status(cntr: Container):
    cntr.reload()
    return ContainerStatus.get_by_value(cntr.status)


def wait_for_container_status(cntr: Container, status: ContainerStatus, timeout=DOCKER_TIMEOUT):

    wait(lambda: get_container_status(cntr) is status,
         timeout_seconds=timeout,
         waiting_for=f"required container status: {status}\n"
                     f"actual container status: {get_container_status(cntr)}")


def wait_for_running_status(container, timeout=DOCKER_TIMEOUT):
    wait_for_container_status(cntr=container, status=ContainerStatus.RUNNING, timeout=timeout)


def wait_for_exited_status(container, timeout=DOCKER_TIMEOUT):
    wait_for_container_status(cntr=container, status=ContainerStatus.EXITED, timeout=timeout)


def get_service_url_base(container, exposed_port):
    wait_for_running_status(container=container)

    exposed = get_from_multilevel_dict(multilevel_dict=container.attrs, key="Ports")
    service_ip_port = exposed.get(f"{exposed_port}/tcp")

    if not service_ip_port:
        raise RuntimeError(f"no host binding port for {exposed_port}")

    ip = service_ip_port[0]["HostIp"]
    port = service_ip_port[0]["HostPort"]

    return f"http://{ip}:{port}"


def get_free_port():
    sock = socket.socket()
    sock.bind(('', 0))
    return sock.getsockname()[1]

