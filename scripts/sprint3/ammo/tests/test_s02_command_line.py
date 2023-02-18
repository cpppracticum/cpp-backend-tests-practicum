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


def test_tick_miss_delta(docker_server):
    request = 'api/v1/game/tick'
    header = {'content-type': 'application/json'}

    res = docker_server.request('POST', header, request)

    assert res.status_code == 400
    assert res.headers['content-type'] == 'application/json'
    assert res.headers['cache-control'] == 'no-cache'
    res_json = res.json()
    print(res_json)
    assert res_json['code'] == 'invalidArgument'
    assert res_json.get('message')


@pytest.mark.parametrize('delta', {0.0, '0', True})
def test_tick_invalid_type_delta(docker_server, delta):
    request = 'api/v1/game/tick'
    header = {'content-type': 'application/json'}

    data = {"timeDelta": delta}
    res = docker_server.request('POST', header, request, json=data)

    assert res.status_code == 400
    assert res.headers['content-type'] == 'application/json'
    assert res.headers['cache-control'] == 'no-cache'
    res_json = res.json()
    print(res_json)
    assert res_json['code'] == 'invalidArgument'
    assert res_json.get('message')


@pytest.mark.parametrize('method', ['GET', 'OPTIONS', 'HEAD', 'PUT', 'PATCH', 'DELETE'])
def test_tick_invalid_verb(docker_server, method):
    request = 'api/v1/game/tick'
    header = {'content-type': 'application/json'}
    res = docker_server.request(method, header, request)
    print(res.headers)
    assert res.status_code == 405
    assert res.headers['content-type'] == 'application/json'
    assert res.headers['cache-control'] == 'no-cache'

    if method != 'HEAD':
        res_json = res.json()
        assert res_json['code'] == 'invalidMethod'
        assert res_json.get('message')


@pytest.mark.randomize(min_num=0, max_num=10000, ncalls=10)
def test_tick_success(docker_server, delta: int):
    request = 'api/v1/game/tick'
    header = {'content-type': 'application/json'}
    data = {"timeDelta": delta}
    res = docker_server.request('POST', header, request, json=data)

    assert res.status_code == 200
    assert res.headers['content-type'] == 'application/json'
    assert res.headers['cache-control'] == 'no-cache'

    res_json = res.json()
    print(res_json)
    assert res_json == dict()


