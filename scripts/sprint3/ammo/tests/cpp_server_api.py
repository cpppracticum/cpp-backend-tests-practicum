import json
import os
import re
import time

import docker
import docker.errors

import requests

from urllib.parse import urljoin
from typing import Optional, Tuple, List, Union, Type, KeysView, Any


class ServerException(Exception):
    def __init__(self, message: str, data: Any):
        super().__init__()
        self.__message = message
        self.__data = data
        self.args = message, data

    def message(self):
        return self.__message

    def data(self):
        return self.__data

    def __str__(self):
        return f"{self.message}: {json.dumps(self.data)}"


class DataInconsistency(ServerException):
    """
    Given data doesn't have all the expected fields or values are not sufficient
    """


class UnexpectedData(DataInconsistency):
    """
    One of the field is missing
    """

    def __init__(self, parent_object: str, expected: Any, given: Any):
        super().__init__(f"{parent_object} has unexpected data",
                         {'expected': expected, 'given': given})
        self.__parent_object = parent_object
        self.__expected = expected
        self.__given = given
        self.args = parent_object, expected, given

    def parent_object(self):
        return self.__parent_object

    def expected(self):
        return self.__expected

    def given(self):
        return self.__given

    def __str__(self):
        return f"{self.parent_object} has unexpected data:\n{json.dumps(self.expected)} was expected, " \
               f"but {json.dumps(self.given)} was given"


class WrongFields(UnexpectedData):
    """
    One of the field is missing
    """

    def __str__(self):
        return f"{self.parent_object} has wrong fields:\n{json.dumps(self.expected)} was expected, " \
               f"but {json.dumps(self.given)} was given"


class WrongType(DataInconsistency):
    def __init__(self, parent_object: str, expected_type: Union[Type, List[Type]], given_type: Type):

        expected_type = [t.__name__ for t in list(expected_type)]

        super().__init__(f"{parent_object} has wrong fields",
                         {'expected type': expected_type, 'given type': given_type.__name__})

        self.__parent_object = parent_object
        self.__expected_type = expected_type
        self.__given_type = given_type
        self.args = parent_object, expected_type, given_type

    def parent_object(self):
        return self.__parent_object

    def expected_type(self):
        return self.__expected_type

    def given_type(self):
        return self.__given_type

    def __str__(self):
        return f"{self.parent_object} has wrong type:\n{json.dumps(self.expected_type)} was expected, " \
               f"but it's {json.dumps(self.given_type.__name__)}"


class BadRequest(ServerException):
    """
    The request was bad - token is wrong or missing, url isn't valid, etc.
    """


class PortIsAllocated(ServerException):
    """
    Docker container can't use the given port, because it's already allocated
    """


class CppServer:

    def __init__(self,
                 server_domain: str,
                 port: Union[str, int] = '8080',
                 image: Optional[str] = None,
                 start_pattern: Optional[str] = '[Ss]erver (has )?started',
                 **extra_kwargs):
        self.url = f'http://{server_domain}:{port}'
        self.port = port

        if image is None:
            self.container = None
            return

        client = docker.from_env()
        inspector = docker.APIClient()
        docker_network = os.environ.get('DOCKER_NETWORK')

        kwargs = {
            'detach': True,
            'auto_remove': True,
        }

        if 'container_args' in extra_kwargs:
            container_args = extra_kwargs.pop('container_args')
        else:
            container_args = None

        if docker_network:
            kwargs['network'] = docker_network

        kwargs.update(extra_kwargs)

        try:
            if container_args:
                self.container = client.containers.run(image, list(container_args), **kwargs)
            else:
                self.container = client.containers.run(image, **kwargs)
            if self.container is None:
                raise ServerException('Container does not exist', None)
            pattern = start_pattern
            logs = self.container.logs().decode()
            start_time = time.time()
            while re.search(pattern, logs) is None:
                time.sleep(1)
                logs = self.container.logs().decode()
                current_time = time.time()
                if current_time - start_time >= 3:
                    raise ServerException('Cannot get the right start phrase from the container.', {'logs': logs})

            # Для доступа в контейнер по имени нужно переприсвоить ему выданное (100% свободное уникальное) имя
            name = inspector.inspect_container(self.container.id)['Name'][1:]  # Для этого вытаскиваем текущее имя
            # Присваиваем имя на символ короче, чтобы не получить ошибку, что текущее имя уже занято
            self.container.rename(name[:-1])
            self.container.rename(name)     # Присваиваем изначальное имя, чтобы иметь доступ по нему

            if server_domain != '127.0.0.1':
                # Если работаем в сети докера - обращаемся по имени
                server_domain = inspector.inspect_container(self.container.id)['Name'][1:]
            else:
                # Иначе - по IP адресу контейнера
                server_domain = inspector.inspect_container(self.container.id)['NetworkSettings']['IPAddress']

            # Переприсваиваем url для запросов
            self.url = f'http://{server_domain}:{port}'

        except docker.errors.APIError:
            self.container = None

        self.cursor = 0

    def __enter__(self, **kwargs):
        self.__init__(**kwargs)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__del__()

    def __del__(self):
        if self.container is not None:
            try:
                self.container.stop()
            except docker.errors.NotFound:
                pass

    def get_line(self):
        logs: str = self.container.logs().decode()
        lines = logs.split('\n')
        try:
            line = lines[self.cursor]
            self.cursor += 1
            return line
        except IndexError:
            return None

    def get_log(self):
        attempt = 1
        while attempt <= 3:
            line = self.get_line()
            if line is not None:
                return json.loads(line)
            attempt += 1
            time.sleep(0.1)   # In case the server haven't posted logs yet, but will do it soon
        return None

    def request(self, method, header, url, **kwargs):
        try:
            req = requests.Request(method, urljoin(self.url, url), headers=header, **kwargs).prepare()
            with requests.Session() as session:
                return session.send(req)
        except Exception as ex:
            print(ex)

    def get(self, endpoint):
        return requests.get(urljoin(self.url, endpoint))

    def post(self, endpoint, data):
        return requests.post(urljoin(self.url, endpoint), data)

    def get_maps(self) -> Optional[List[dict]]:
        request = 'api/v1/maps'
        res: requests.Response = self.get(request)
        self.validate_response(res)
        res_json: List[dict] = res.json()

        CppServer.assert_type('Map list', list, res_json)

        for m in res_json:
            CppServer.assert_fields('Map', ['id', 'name'], m.keys())
            CppServer.assert_type('Map id', str, m['id'])
            CppServer.assert_type('Map name', str, m['name'])

        return res_json

    def get_map(self, map_id: str) -> Optional[dict]:
        request = 'api/v1/maps/' + map_id
        res: requests.Response = self.get(request)
        self.validate_response(res)
        self.validate_map(res.json())
        return res.json()

    def join(self, player_name: str, map_id: str) -> Tuple[str, int]:
        request = 'api/v1/game/join'
        header = {'content-type': 'application/json'}
        data = {"userName": player_name, "mapId": map_id}
        res = self.request('POST', header, request, json=data)
        res_json: dict = res.json()

        CppServer.assert_fields('Join game response', ['authToken', 'playerId'], res_json.keys())

        token = res_json['authToken']
        self.validate_token(token)

        player_id = res_json['playerId']
        CppServer.assert_type('Player id', int, player_id)

        return token, player_id

    def add_player(self, player_name: str, map_id: str) -> Tuple[str, int]:
        params = self.join(player_name, map_id)
        # Temporary "fix"
        return params

    def get_state(self, token: str) -> Optional[dict]:
        request = '/api/v1/game/state'
        header = {'content-type': 'application/json',
                  'Authorization': f'Bearer {token}'}

        res = self.request('GET', header, request)
        self.validate_response(res)
        res_json = res.json()
        self.validate_state(res_json)
        return res_json

    def get_player_state(self, token: str, player_id: int) -> Optional[dict]:
        game_session_state = self.get_state(token)

        self.assert_type('Game session state', dict, game_session_state)
        self.assert_fields('Game session state', 'players', game_session_state.keys())

        players = game_session_state.get('players')

        self.assert_type('Players state', dict, players)
        state = players.get(str(player_id))

        if state is None:
            raise DataInconsistency('Game state doesn\'t have the given player id',
                                    {'player_id': players, 'game_state': game_session_state})

        self.validate_player_state(state)

        return state

    def move(self, token: str, direction: str):
        request = '/api/v1/game/player/action'
        header = {'content-type': 'application/json', 'Authorization': f'Bearer {token}'}
        data = {"move": direction}
        res = self.request('POST', header, request, json=data)
        self.validate_response(res)

    def tick(self, ticks: int):
        request = 'api/v1/game/tick'
        header = {'content-type': 'application/json'}
        data = {"timeDelta": ticks}
        res = self.request('POST', header, request, json=data)
        self.validate_response(res)

    @staticmethod
    def assert_type(obj_name: str, expected_types: Union[Type, List[Type]], obj: any):
        if type(expected_types) not in {list, tuple, set}:
            expected_types = [expected_types]
        if type(obj) not in expected_types:
            raise WrongType(obj_name, expected_types, type(obj))

    @staticmethod
    def assert_fields(object_name, expected_keys: Union[list, str, KeysView], given_keys: KeysView):
        if type(expected_keys) == str:
            expected_keys = [expected_keys]
        else:
            expected_keys = list(expected_keys)

        for key in expected_keys:
            if key not in given_keys:
                raise WrongFields(object_name, list(expected_keys), list(given_keys))

    # Wil be rewritten soon
    @staticmethod
    def validate_response(res: requests.Response):
        if res.status_code != 200:
            raise BadRequest('Status code isn\'t OK', {'status code': res.status_code, 'response': res.content})

        CppServer.assert_fields('Response headers',
                                ['content-type', 'cache-control', 'content-length'],
                                res.headers.keys())

        if res.headers['content-type'] != 'application/json':
            raise UnexpectedData('Content-type', 'application/json', res.headers['content-type'])

        if res.headers['cache-control'] != 'no-cache':
            raise UnexpectedData('Cache-control', 'no-cache', res.headers['cache-control'])

        if res.request.method != 'HEAD':
            if int(res.headers['content-length']) != len(res.content):
                raise UnexpectedData('Headers\' content-length', len(res.content), int(res.headers['content-length']))
        else:
            if res.headers['content-length'] != 0:
                raise UnexpectedData('Headers\' content-length for head request should be zero',
                                     0, int(res.headers['content-length']))

        try:
            res.json()
        except json.decoder.JSONDecodeError as je:
            raise DataInconsistency('The response has badly encoded JSON',
                                    {'response content': res.content, 'JSON decoder error': [je.msg, je.doc, je.pos]})

    @staticmethod
    def validate_map(m: dict):
        expected = {'id': str, 'name': str, 'roads': list, 'buildings': list, 'offices': list}

        CppServer.assert_fields('Map', expected.keys(), m.keys())

        for key in expected.keys():
            CppServer.assert_type(key, expected[key], m[key])

        extra = {'dogSpeed': float}

        for key in extra:
            if key in m.keys():
                CppServer.assert_type(key, extra[key], m[key])

        dog_speed = m.get('dogSpeed')
        if dog_speed is not None:
            if dog_speed < 0:
                raise DataInconsistency('Dog speed can\'t be negative', {'dog speed': dog_speed})

        for road in m['roads']:
            road: dict
            CppServer.assert_type('Road', dict, road)

            if road.keys() != {'x0', 'y0', 'x1'} and road.keys() != {'x0', 'y0', 'y1'}:
                raise WrongFields('Road', '["x0", "y0", "x1"] or ["x0", "y0", "y1"]', list(road.keys()))

            for coordinate in road:
                CppServer.assert_type(f'Road coordinate {coordinate}', [float, int], road[coordinate])

        for building in m['buildings']:
            building: dict

            CppServer.assert_type('Building on the map', dict, building)
            CppServer.assert_fields('Building on the map', ['x', 'y', 'w', 'h'], building.keys())

            for field in building:
                CppServer.assert_type(f'Building field {field}', [float, int], building[field])
                if field in ['w', 'h']:
                    if building[field] <= 0:
                        raise DataInconsistency('Building size is\'t positive', {'building': building})

        for office in m['offices']:
            office: dict
            CppServer.assert_type('Office', dict, office)

            expected = {'id': str, 'x': [float, int], 'y': [float, int],
                        'offsetX': [float, int], 'offsetY': [float, int]}

            CppServer.assert_fields('Office on the map', expected.keys(), office.keys())

            for field in expected:
                CppServer.assert_type(f'Office field {field}', expected[field], office[field])

    @staticmethod
    def validate_token(token: str):
        try:
            int(token, 16)
        except ValueError:
            raise DataInconsistency('Token is invalid, it should be a hex value', {'token': token})

    @staticmethod
    def validate_state(res_json: dict):
        CppServer.assert_type('Game state', dict, res_json)
        players = res_json.get('players')
        CppServer.assert_type('Game state, players', dict, players)
        for player_id in players:
            CppServer.assert_type('Player id', [str, int], player_id)
            player: dict = players[player_id]

            CppServer.validate_player_state(player)

    @staticmethod
    def validate_player_state(state: dict):

        CppServer.assert_type('player_id', dict, state)

        expected = {'pos': list, 'speed': list, 'dir': str}
        for key in expected:
            CppServer.assert_fields(f'Player state', expected.keys(), state.keys())
            CppServer.assert_type(key, expected[key], state[key])

        for coordinate in state['pos']:
            CppServer.assert_type('Player position', float, coordinate)
        for coordinate in state['speed']:
            CppServer.assert_type('Player speed', float, coordinate)

        CppServer.assert_type('Player direction', str, state['dir'])
        expected_dirs = ['R', 'L', 'U', 'D', '']
        if state['dir'] not in expected_dirs:
            raise UnexpectedData('Player direction', ['R', 'L', 'U', 'D', ''], state['dir'])
