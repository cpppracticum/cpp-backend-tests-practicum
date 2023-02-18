import pytest


def get_maps(docker_server):
    request = 'api/v1/maps'
    res = docker_server.get(request)
    return res.json()


def join_to_map(docker_server, user_name, map_id):
    request = 'api/v1/game/join'
    header = {'content-type': 'application/json'}
    data = {"userName": user_name, "mapId": map_id}
    return docker_server.request('POST', header, request, json=data)


def test_state_miss_token(docker_server):
    request = 'api/v1/game/state'
    header = {'content-type': 'application/json'}
    res = docker_server.request('GET', header, request)
    assert res.status_code == 401
    assert res.headers['content-type'] == 'application/json'
    assert res.headers['cache-control'] == 'no-cache'
    res_json = res.json()
    print(res_json)
    assert res_json['code'] == 'invalidToken'
    assert res_json.get('message')


@pytest.mark.randomize(min_length=0, max_length=31, str_attrs=('hexdigits',), ncalls=10)
def test_state_invalid_token(docker_server, token: str):
    request = 'api/v1/game/state'
    header = {'content-type': 'application/json', 'authorization': f'Bearer {token}'}
    res = docker_server.request('GET', header, request)
    assert res.status_code == 401
    assert res.headers['content-type'] == 'application/json'
    assert res.headers['cache-control'] == 'no-cache'
    res_json = res.json()
    print(res_json)
    assert res_json['code'] == 'invalidToken'
    assert res_json.get('message')


@pytest.mark.randomize(fixed_length=32, str_attrs=('hexdigits',), ncalls=10)
def test_state_unknown_token(docker_server, token: str):
    request = 'api/v1/game/state'
    header = {'content-type': 'application/json', 'authorization': f'Bearer {token}'}
    res = docker_server.request('GET', header, request)
    assert res.status_code == 401
    assert res.headers['content-type'] == 'application/json'
    assert res.headers['cache-control'] == 'no-cache'
    res_json = res.json()
    print(res_json)
    assert res_json['code'] == 'unknownToken'
    assert res_json.get('message')


@pytest.mark.parametrize('method', ['OPTIONS', 'POST', 'PUT', 'PATCH', 'DELETE'])
def test_state_invalid_verb(docker_server, method):
    request = 'api/v1/game/state'
    header = {'content-type': 'application/json', 'authorization': 'Bearer 6516861d89ebfff147bf2eb2b5153ae1'}
    res = docker_server.request(method, header, request)
    assert res.status_code == 405
    assert res.headers['content-type'] == 'application/json'
    assert res.headers['cache-control'] == 'no-cache'
    for allow in res.headers['allow'].split(','):
        assert allow.strip().upper() in {'GET', 'HEAD'}
    res_json = res.json()
    print(res_json)
    assert res_json['code'] == 'invalidMethod'
    assert res_json.get('message')


@pytest.mark.parametrize('method', ['GET', 'HEAD'])
def test_state_success(docker_server, method):
    maps = get_maps(docker_server)
    res = join_to_map(docker_server, "User1", maps[0]['id'])
    token = res.json()['authToken']

    request = 'api/v1/game/state'
    header = {'content-type': 'application/json', 'authorization': f'Bearer {token}'}

    res = docker_server.request(method, header, request)

    assert res.status_code == 200
    assert res.headers['content-type'] == 'application/json'
    assert res.headers['cache-control'] == 'no-cache'

    if method != 'HEAD':
        res_json = res.json()
        for _, player in res_json['players'].items():
            assert player['speed'] == [0.0, 0.0]
            assert player['dir'] == 'U'
