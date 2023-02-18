import pytest
import conftest as utils


def test_join_invalid_map(docker_server):
    request = 'api/v1/game/join'
    header = {'content-type': 'application/json'}
    data = {"userName": "Harry Potter", "mapId": '  invalid  '}
    res = docker_server.request('POST', header, request, json=data)
    assert res.status_code == 404
    assert res.headers['content-type'] == 'application/json'
    assert res.headers['cache-control'] == 'no-cache'
    res_json = res.json()

    assert res_json['code'] == 'mapNotFound'
    assert res_json.get('message')


def test_join_invalid_user_name(docker_server):
    request = 'api/v1/game/join'
    header = {'content-type': 'application/json'}
    maps = utils.get_maps(docker_server)
    data = {"userName": "", "mapId": maps[0]['id']}
    res = docker_server.request('POST', header, request, json=data)
    assert res.status_code == 400
    assert res.headers['content-type'] == 'application/json'
    assert res.headers['cache-control'] == 'no-cache'
    res_json = res.json()

    assert res_json['code'] == 'invalidArgument'
    assert res_json.get('message')


def test_join_miss_user_name(docker_server):
    request = 'api/v1/game/join'
    header = {'content-type': 'application/json'}
    maps = utils.get_maps(docker_server)
    data = {"mapId": maps[0]['id']}
    res = docker_server.request('POST', header, request, json=data)
    assert res.status_code == 400
    assert res.headers['content-type'] == 'application/json'
    assert res.headers['cache-control'] == 'no-cache'
    res_json = res.json()

    assert res_json['code'] == 'invalidArgument'
    assert res_json.get('message')


def test_join_miss_map_id(docker_server):
    request = 'api/v1/game/join'
    header = {'content-type': 'application/json'}
    data = {"userName": "Harry Potter"}
    res = docker_server.request('POST', header, request, json=data)
    assert res.status_code == 400
    assert res.headers['content-type'] == 'application/json'
    assert res.headers['cache-control'] == 'no-cache'
    res_json = res.json()

    assert res_json['code'] == 'invalidArgument'
    assert res_json.get('message')


def test_join_miss_data(docker_server):
    request = 'api/v1/game/join'
    header = {'content-type': 'application/json'}
    data = {}
    res = docker_server.request('POST', header, request, json=data)
    assert res.status_code == 400
    assert res.headers['content-type'] == 'application/json'
    assert res.headers['cache-control'] == 'no-cache'
    res_json = res.json()

    assert res_json['code'] == 'invalidArgument'
    assert res_json.get('message')


def test_join_invalid_data(docker_server):
    request = 'api/v1/game/join'
    header = {'content-type': 'application/json'}
    data = {"userName": "", "mapId": '   invalid   '}
    res = docker_server.request('POST', header, request, json=data)
    assert res.status_code == 400
    assert res.headers['content-type'] == 'application/json'
    assert res.headers['cache-control'] == 'no-cache'
    res_json = res.json()

    assert res_json['code'] == 'invalidArgument'
    assert res_json.get('message')


@pytest.mark.parametrize('method', ['GET', 'OPTIONS', 'HEAD', 'PUT', 'PATCH', 'DELETE'])
def test_join_invalid_verb(docker_server, method):
    request = 'api/v1/game/join'
    header = {'content-type': 'application/json'}
    res = docker_server.request(method, header, request)

    assert res.status_code == 405
    assert res.headers['content-type'] == 'application/json'
    assert res.headers['cache-control'] == 'no-cache'
    utils.check_allow(res.headers['allow'], {'POST'})

    if method != 'HEAD':
        res_json = res.json()

        assert res_json['code'] == 'invalidMethod'
        assert res_json.get('message')
    else:
        assert '' == res.text


@pytest.mark.randomize(min_length=1, max_length=100, str_attrs=('printable',), ncalls=10)
def test_join_success(docker_server, name: str):
    maps = utils.get_maps(docker_server)
    res = utils.join_to_map(docker_server, name, maps[0]['id'])
    assert res.status_code == 200
    assert res.headers['content-type'] == 'application/json'
    assert res.headers['cache-control'] == 'no-cache'
    res_json = res.json()

    assert isinstance(res_json['playerId'], int)
    assert len(res_json['authToken']) == 32
    assert int(res_json['authToken'], 16)


def test_players_miss_token(docker_server):
    request = 'api/v1/game/players'
    header = {'content-type': 'application/json'}
    res = docker_server.request('GET', header, request)
    assert res.status_code == 401
    assert res.headers['content-type'] == 'application/json'
    assert res.headers['cache-control'] == 'no-cache'
    res_json = res.json()

    assert res_json['code'] == 'invalidToken'
    assert res_json.get('message')


def test_players_invalid_token(docker_server):
    request = 'api/v1/game/players'
    header = {'content-type': 'application/json', 'authorization': 'Bearer'}
    res = docker_server.request('GET', header, request)
    assert res.status_code == 401
    assert res.headers['content-type'] == 'application/json'
    assert res.headers['cache-control'] == 'no-cache'
    res_json = res.json()

    assert res_json['code'] == 'invalidToken'
    assert res_json.get('message')


def test_players_unknown_token(docker_server):
    request = 'api/v1/game/players'
    header = {'content-type': 'application/json', 'authorization': 'Bearer 6516861d89ebfff147bf2eb2b5153ae1'}
    res = docker_server.request('GET', header, request)
    assert res.status_code == 401
    assert res.headers['content-type'] == 'application/json'
    assert res.headers['cache-control'] == 'no-cache'
    res_json = res.json()

    assert res_json['code'] == 'unknownToken'
    assert res_json.get('message')


@pytest.mark.parametrize('method', ['OPTIONS', 'POST', 'PUT', 'PATCH', 'DELETE'])
def test_players_invalid_verb(docker_server, method):
    request = 'api/v1/game/players'
    header = {'content-type': 'application/json', 'authorization': 'Bearer 6516861d89ebfff147bf2eb2b5153ae1'}
    res = docker_server.request(method, header, request)
    assert res.status_code == 405
    assert res.headers['content-type'] == 'application/json'
    assert res.headers['cache-control'] == 'no-cache'
    utils.check_allow(res.headers['allow'], {'GET', 'HEAD'})

    res_json = res.json()

    assert res_json['code'] == 'invalidMethod'
    assert res_json.get('message')


@pytest.mark.parametrize('method', ['GET', 'HEAD'])
def test_players_success(docker_server, method):
    maps = utils.get_maps(docker_server)
    res = utils.join_to_map(docker_server, 'User1', maps[0]['id'])
    token1 = res.json()['authToken']
    res = utils.join_to_map(docker_server, 'User2', maps[0]['id'])
    token2 = res.json()['authToken']

    request = 'api/v1/game/players'
    header = {'content-type': 'application/json', 'authorization': f'Bearer {token1}'}
    res1 = docker_server.request(method, header, request)
    assert res1.status_code == 200
    assert res1.headers['content-type'] == 'application/json'
    assert res1.headers['cache-control'] == 'no-cache'

    header = {'content-type': 'application/json', 'authorization': f'Bearer {token2}'}
    res2 = docker_server.request(method, header, request)
    assert res2.status_code == 200
    assert res2.headers['content-type'] == 'application/json'
    assert res2.headers['cache-control'] == 'no-cache'

    if method != 'HEAD':
        res1_json = res1.json()
        res2_json = res2.json()
        assert res1_json == res2_json
    else:
        assert '' == res1.text
        assert '' == res2.text
