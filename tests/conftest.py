import os
import json
import pathlib
import jsonschema

import pytest

from xprocess import ProcessStarter
from pathlib import Path
from contextlib import contextmanager
from typing import Set


from cpp_server_api import CppServer as Server
from cpp_server_api import ServerException

START_PATTERN = '[Ss]erver (has )?started'
JSON_SCHEMA_PATH = os.environ.get('JSON_SCHEMA_PATH')


def get_maps_from_config_file(config: Path):
    return json.loads(config.read_text())['maps']


def pytest_generate_tests(metafunc):
    config_path = os.environ.get('CONFIG_PATH')

    if 'map_dict' in metafunc.fixturenames:
        if config_path:
            config_path = Path(config_path)
            metafunc.parametrize(
                'map_dict',
                [
                    pytest.param(map_dict, id=map_dict['name'])
                    for map_dict in get_maps_from_config_file(config_path)
                ],
            )
    if 'config' in metafunc.fixturenames:
        if config_path:
            config_path = Path(config_path)
            with open(config_path, 'r') as f:
                config = json.load(f)
            metafunc.parametrize(
                'config',
                config
            )
    if 'map_id' in metafunc.fixturenames:
        if config_path:
            config_path = Path(config_path)
            metafunc.parametrize(
                'map_id',
                [
                    pytest.param(map_dict['id'], id=map_dict['id'])
                    for map_dict in json.loads(config_path.read_text())['maps']
                ],
            )


@pytest.fixture(scope='module')
def server(xprocess):
    with _make_server(xprocess) as result:
        yield result


@contextmanager
def _make_server(xprocess):
    commands = os.environ['COMMAND_RUN'].split()
    server_domain = os.environ.get('SERVER_DOMAIN', '127.0.0.1')
    server_port = os.environ.get('SERVER_PORT', '8080')
    config_path = os.environ.get('CONFIG_PATH')

    if config_path is not None and JSON_SCHEMA_PATH is not None:
        with open(config_path, 'r') as f:
            config = json.load(f)
        with open(JSON_SCHEMA_PATH, 'r') as f:
            schema = json.load(f)
        print(config)
        print(schema)
        jsonschema.validate(config, schema)

    class Starter(ProcessStarter):
        pattern = START_PATTERN
        args = commands

    _, output_path = xprocess.ensure("server", Starter)

    yield Server(server_domain, server_port)

    xprocess.getinfo("server").terminate()


@pytest.fixture(scope='function')
def server_one_test(xprocess):
    with _make_server(xprocess) as result:
        yield result


@pytest.fixture(scope='function')
def docker_server():
    server_domain = os.environ.get('SERVER_DOMAIN', '127.0.0.1')
    image_name = os.environ['IMAGE_NAME']
    port = os.environ.get('SERVER_PORT', '8080')
    config_path = os.environ.get('CONFIG_PATH')

    if config_path is not None and JSON_SCHEMA_PATH is not None:
        with open(config_path, 'r') as f:
            config = json.load(f)
        with open(JSON_SCHEMA_PATH, 'r') as f:
            schema = json.load(f)
        print()
        jsonschema.validate(config, schema)

    extra_kwargs = {}

    if 'ENTRYPOINT' in os.environ:
        extra_kwargs['entrypoint'] = os.environ['ENTRYPOINT']
    if 'CONTAINER_ARGS' in os.environ:
        extra_kwargs['container_args'] = os.environ['CONTAINER_ARGS'].split(' ')
    server = Server(server_domain, port, image_name, start_pattern=START_PATTERN, **extra_kwargs)

    return server


def get_config():
    try:
        config_path = os.environ['CONFIG_PATH']
        return json.loads(pathlib.Path(config_path).read_text())
    except KeyError:
        raise ServerException('Config path is not given!', {'given variables': os.environ.keys()})
    except FileNotFoundError:
        raise ServerException('Config file not found!', {'config_path': os.environ.get('CONFIG_PATH')})
    except json.decoder.JSONDecodeError as ex:
        raise ServerException('Cannot parse config file', ex)


def get_start_pattern():
    return START_PATTERN


def get_maps(server):
    request = 'api/v1/maps'
    res = server.get(request)
    return res.json()


def join_to_map(server, user_name: str, map_id: str):
    request = 'api/v1/game/join'
    header = {'content-type': 'application/json'}
    data = {"userName": user_name, "mapId": map_id}
    return server.request('POST', header, request, json=data)


def sort_by_id(lst: list):
    return sorted(lst, key=lambda x: x['id'])


def get_maps_from_config(config: dict):
    return sort_by_id([
        {'id': map_dict['id'], 'name': map_dict['name']}
        for map_dict
        in config['maps']
    ])


def tick(server, delta: int):
    request = 'api/v1/game/tick'
    header = {'content-type': 'application/json'}
    data = {"timeDelta": delta}
    res = server.request('POST', header, request, json=data)
    assert res.status_code == 200
    return res


def check_allow(header_allow: str, allows: Set[str]):
    expected = set(verb.strip() for verb in header_allow.split(','))
    assert expected == allows
