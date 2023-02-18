import pytest
import conftest as utils
from game_server import Road, Point


defaultBagCapacity = 3


@pytest.mark.parametrize('method', ['OPTIONS', 'POST', 'PUT', 'PATCH', 'DELETE'])
def test_map_invalid_verb(docker_server, method, map_dict):
    map_id = map_dict['id']
    header = {}
    request = f'api/v1/maps/{map_id}'
    res = docker_server.request(method, header, f'/{request}')

    assert res.status_code == 405
    assert res.headers['content-type'] == 'application/json'
    assert res.headers['cache-control'] == 'no-cache'
    utils.check_allow(res.headers['allow'], {'GET', 'HEAD'})

    res_json = res.json()
    assert res_json['code'] == 'invalidMethod'
    assert res_json.get('message')


@pytest.mark.parametrize('method', ['GET', 'HEAD'])
@pytest.mark.randomize(min_length=1, max_length=15, str_attrs=('digits', 'ascii_letters'), ncalls=3)
def test_map_not_found(docker_server, method, map_id_bad: str):
    header = {}
    request = f'api/v1/maps/__{map_id_bad}'
    res = docker_server.request(method, header, f'/{request}')

    assert res.status_code == 404
    assert res.headers['content-type'] == 'application/json'
    assert res.headers['cache-control'] == 'no-cache'

    if method != 'HEAD':
        res_json = res.json()
        print(res_json)

        assert res_json['code'] == 'mapNotFound'
        assert res_json.get('message')
    else:
        assert '' == res.text


@pytest.mark.parametrize('method', ['GET', 'HEAD'])
def test_map_success(docker_server, method, map_dict):
    map_dict.pop('dogSpeed', None)
    header = {}
    request = f'api/v1/maps/{map_dict["id"]}'
    res = docker_server.request(method, header, f'/{request}')

    assert res.status_code == 200
    assert res.headers['content-type'] == 'application/json'

    if method != 'HEAD':
        assert map_dict == res.json()
    else:
        assert '' == res.text


@pytest.mark.parametrize('method', ['OPTIONS', 'POST', 'PUT', 'PATCH', 'DELETE'])
def test_state_invalid_verb(docker_server, method):
    header = {}
    request = 'api/v1/game/state'
    res = docker_server.request(method, header, f'/{request}')

    assert res.status_code == 405
    assert res.headers['content-type'] == 'application/json'
    assert res.headers['cache-control'] == 'no-cache'
    utils.check_allow(res.headers['allow'], {'GET', 'HEAD'})

    res_json = res.json()
    assert res_json['code'] == 'invalidMethod'
    assert res_json.get('message')


def is_point_on_roads(roads: dict, point: list):
    return any((Road(road).is_on_the_road(Point(*point)) for road in roads))


def add_user_and_wait_loot(docker_server, name, map_id):
    res = utils.join_to_map(docker_server, name, map_id)
    token = res.json()['authToken']
    utils.tick(docker_server, 5000*1000)
    utils.tick(docker_server, 5000*1000)
    utils.tick(docker_server, 5000*1000)
    utils.tick(docker_server, 5000*1000)
    return token


@pytest.mark.parametrize('method', ['HEAD', 'GET'])
def test_state_success(docker_server, method, map_dict):
    map_id = map_dict['id']

    for i, name in enumerate(['user1', 'user2']):
        token = add_user_and_wait_loot(docker_server, name, map_id)

        request = 'api/v1/game/state'
        header = {'content-type': 'application/json', 'authorization': f'Bearer {token}'}
        res = docker_server.request(method, header, request)

        assert res.status_code == 200
        assert res.headers['content-type'] == 'application/json'
        assert res.headers['cache-control'] == 'no-cache'

        if method != 'HEAD':
            res_json = res.json()
            print(res_json)
            for _, player in res_json['players'].items():
                assert isinstance(player['pos'], list)
                assert len(player['pos']) == 2
                assert isinstance(player['pos'][0], float)
                assert isinstance(player['pos'][1], float)
                assert is_point_on_roads(map_dict['roads'], player['pos'])

                assert isinstance(player['speed'], list)
                assert len(player['speed']) == 2
                assert isinstance(player['speed'][0], float)
                assert isinstance(player['speed'][1], float)
                assert player['speed'] == [0.0, 0.0]

                assert isinstance(player['dir'], str)
                assert len(player['dir']) == 1
                assert player['dir'] == 'U'

                assert isinstance(player['bag'], list)
                assert len(player['bag']) <= defaultBagCapacity
                for item in player['bag']:
                    assert isinstance(item['id'], int)
                    assert isinstance(item['type'], int)

            assert res_json['lostObjects']
            assert isinstance(res_json['lostObjects'], dict)
            assert len(res_json['lostObjects']) == i+1

            for _, obj in res_json['lostObjects'].items():
                assert obj['type'] in set(range(len(map_dict['lootTypes'])))
                assert isinstance(obj['pos'], list)
                assert len(obj['pos']) == 2
                assert isinstance(obj['pos'][0], float)
                assert isinstance(obj['pos'][1], float)
                assert is_point_on_roads(map_dict['roads'], obj['pos'])
        else:
            assert '' == res.text
