from conftest import get_config

map_not_found = {
    "code": "mapNotFound",
    "message": "Map not found"
}

bad_request = {
    "code": "badRequest",
    "message": "Bad request"
}


def get_maps_answer(config):
    ans = []
    for m in config['maps']:
        ans.append({
            'id': m['id'],
            'name': m['name']
        })
    return ans


def get_map_info_ans(map_dict: dict):
    keys = ['id', 'name', 'roads', 'buildings', 'offices']
    ans = dict()
    for k in keys:
        ans.update({k: map_dict[k]})
    return ans


def test_list(docker_server):
    config = get_config()
    request = 'api/v1/maps'
    res = docker_server.get(f'/{request}')
    assert res.status_code == 200
    assert res.headers['content-type'] == 'application/json'
    assert res.json() == get_maps_answer(config)


def test_info(docker_server, map_dict):
    m = map_dict['id']
    request = f"api/v1/maps/{m}"
    res = docker_server.get(f'/{request}')
    assert res.status_code == 200
    assert res.headers['content-type'] == 'application/json'
    assert res.json() == get_map_info_ans(map_dict)


def test_map_not_found(docker_server):
    request = 'api/v1/maps/map33'
    res = docker_server.get(f'/{request}')
    assert res.status_code == 404
    assert res.headers['content-type'] == 'application/json'
    assert res.json()["code"] == map_not_found["code"]


def test_bad_request(docker_server):
    request = 'api/v333/maps/map1'
    res = docker_server.get(f'/{request}')
    assert res.status_code == 400
    assert res.headers['content-type'] == 'application/json'
    assert res.json()["code"] == bad_request["code"]
