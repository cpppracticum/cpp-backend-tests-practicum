import os
import time
import pytest
from pathlib import Path
from collections import defaultdict
from dataclasses import dataclass
from typing import List

import docker

from contextlib import contextmanager

import conftest as utils

client = docker.from_env()


def get_image_name():
    return os.environ['IMAGE_NAME']


def network_name():
    return os.environ.get('DOCKER_NETWORK')


def volume_path():
    return Path(os.environ['VOLUME_PATH'])


def remove_state_file(state):
    (Path(volume_path()) / state).unlink()


@contextmanager
def run_server(state, remove_state=False):
    server_domain = os.environ.get('SERVER_DOMAIN', '127.0.0.1')
    server_port = os.environ.get('SERVER_PORT', '8080')
    docker_network = os.environ.get('DOCKER_NETWORK')

    entrypoint = [
        "/app/game_server",
        "--config-file", "/app/data/config.json",
        "--www-root", "/app/static/",
        "--state-file", f"/tmp/volume/{state}",
        "--save-state-period", "1000"
    ]
    kwargs = {
        'detach': True,
        'entrypoint': entrypoint,
        'auto_remove': True,
        'ports': {f"{server_port}/tcp": server_port},
        'volumes': {volume_path(): {'bind': '/tmp/volume', 'mode': 'rw'}},
    }
    if docker_network:
        kwargs['network'] = docker_network
    if server_domain != '127.0.0.1':
        kwargs['name'] = server_domain
    container = client.containers.run(
        get_image_name(),
        **kwargs
    )

    for i in range(2000):
        log = container.logs().decode('utf-8')
        if log.find('server started') != -1:
            break
        time.sleep(0.001)

    # server = utils.Server(f'http://{server_domain}:{server_port}/')
    server = utils.Server(server_domain, server_port)

    try:
        yield server, container
    finally:
        try:
            container.stop()
        except docker.errors.APIError:
            pass
        if remove_state:
            remove_state_file(state)


@dataclass
class Cache:
    tokens: List[str] = None
    state: dict = None

    def __post_init__(self):
        self.tokens = list()
        self.state = dict()


@pytest.mark.parametrize('method', ['GET'])
def test_stop(method):
    state_file = 'state'
    cache = defaultdict(Cache)
    with run_server(state_file) as (server, container):
        for map_dict in utils.get_maps_from_config_file(Path(os.environ['CONFIG_PATH'])):
            for name in ['user1', 'user2']:
                map_id = map_dict['id']

                res = utils.join_to_map(server, name, map_id)
                token = res.json()['authToken']

                cache[map_id].tokens.append(token)

        for map_id, item in cache.items():
            token = item.tokens[0]
            request = 'api/v1/game/state'
            header = {'content-type': 'application/json', 'authorization': f'Bearer {token}'}
            res = server.request(method, header, request)
            cache[map_id].state = res.json()

    with run_server(state_file, remove_state=True) as (server, container):
        for item in cache.values():
            for token in item.tokens:
                request = 'api/v1/game/state'
                header = {'content-type': 'application/json', 'authorization': f'Bearer {token}'}
                res = server.request(method, header, request)
                assert res.json() == item.state


@pytest.mark.parametrize('method', ['GET'])
def test_kill(method):
    state_file = 'state'
    cache = defaultdict(Cache)
    with run_server(state_file) as (server, container):
        for map_dict in utils.get_maps_from_config_file(Path(os.environ['CONFIG_PATH'])):
            for name in ['user1', 'user2']:
                map_id = map_dict['id']

                res = utils.join_to_map(server, name, map_id)
                token = res.json()['authToken']

                cache[map_id].tokens.append(token)

        for map_id, item in cache.items():
            token = item.tokens[0]
            request = 'api/v1/game/state'
            header = {'content-type': 'application/json', 'authorization': f'Bearer {token}'}
            res = server.request(method, header, request)
            cache[map_id].state = res.json()

        container.kill()

    with run_server(state_file, remove_state=True) as (server, container):
        for item in cache.values():
            for token in item.tokens:
                request = 'api/v1/game/state'
                header = {'content-type': 'application/json', 'authorization': f'Bearer {token}'}
                res = server.request(method, header, request)
                assert res.json() != item.state


@pytest.mark.parametrize('method', ['GET'])
def test_tick(method):
    state_file = 'state'
    cache = defaultdict(Cache)
    with run_server(state_file) as (server, container):
        for map_dict in utils.get_maps_from_config_file(Path(os.environ['CONFIG_PATH'])):
            for name in ['user1', 'user2']:
                map_id = map_dict['id']

                res = utils.join_to_map(server, name, map_id)
                token = res.json()['authToken']

                cache[map_id].tokens.append(token)

        utils.tick(server, 5000*1000)
        utils.tick(server, 5000*1000)
        utils.tick(server, 5000*1000)

        for map_id, item in cache.items():
            token = item.tokens[0]
            request = 'api/v1/game/state'
            header = {'content-type': 'application/json', 'authorization': f'Bearer {token}'}
            res = server.request(method, header, request)
            cache[map_id].state = res.json()

        container.kill()

    with run_server(state_file, remove_state=True) as (server, container):
        for item in cache.values():
            for token in item.tokens:
                request = 'api/v1/game/state'
                header = {'content-type': 'application/json', 'authorization': f'Bearer {token}'}
                res = server.request(method, header, request)
                assert res.json() == item.state
