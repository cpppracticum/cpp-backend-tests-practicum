import pytest
import conftest as utils

ans_list = [
    {
        "id": "map1",
        "name": "Map 1"
    }
]

ans_info = {
    "id": "map1",
    "name": "Map 1",
    "roads": [
        {
            "x0": 0,
            "y0": 0,
            "x1": 40
        },
        {
            "x0": 40,
            "y0": 0,
            "y1": 30
        },
        {
            "x0": 40,
            "y0": 30,
            "x1": 0
        },
        {
            "x0": 0,
            "y0": 0,
            "y1": 30
        }
    ],
    "buildings": [
        {
            "x": 5,
            "y": 5,
            "w": 30,
            "h": 20
        }
    ],
    "offices": [
        {
            "id": "o0",
            "x": 40,
            "y": 30,
            "offsetX": 5,
            "offsetY": 0
        }
    ]
}

map_not_found = {
    "code": "mapNotFound",
    "message": "Map not found"
}

bad_request = {
    "code": "badRequest",
    "message": "Bad request"
}

# 
# @pytest.mark.parametrize('method', ['OPTIONS', 'POST', 'PUT', 'PATCH', 'DELETE'])
# def test_maps_invalid_verb(server, method):
#     header = {}
#     request = 'api/v1/maps'
#     res = server.request(method, header, f'/{request}')
# 
#     assert res.status_code == 405
#     assert res.headers['content-type'] == 'application/json'
#     assert res.headers['cache-control'] == 'no-cache'
#     utils.check_allow(res.headers['allow'], {'GET', 'HEAD'})
# 
#     res_json = res.json()
# 
#     assert res_json['code'] == 'invalidMethod'
#     assert res_json.get('message')
# 
# 
# @pytest.mark.parametrize('method', ['GET', 'HEAD'])
# def test_maps_success(server, method):
#     header = {}
#     request = 'api/v1/maps'
#     res = server.request(method, header, f'/{request}')
# 
#     assert res.status_code == 200
#     assert res.headers['content-type'] == 'application/json'
#     expected = utils.get_maps_from_config(server.get_config())
# 
#     if method != 'HEAD':
#         assert expected == utils.sort_by_id(res.json())
#     else:
#         assert '' == res.text
# 
# 
# @pytest.mark.parametrize('method', ['OPTIONS', 'POST', 'PUT', 'PATCH', 'DELETE'])
# def test_map_invalid_verb(server, method, map_dict):
#     map_id = map_dict['id']
#     header = {}
#     request = f'api/v1/maps/{map_id}'
#     res = server.request(method, header, f'/{request}')
# 
#     assert res.status_code == 405
#     assert res.headers['content-type'] == 'application/json'
#     assert res.headers['cache-control'] == 'no-cache'
#     utils.check_allow(res.headers['allow'], {'GET', 'HEAD'})
# 
#     res_json = res.json()
#     assert res_json['code'] == 'invalidMethod'
#     assert res_json.get('message')
# 
# 
# @pytest.mark.parametrize('method', ['GET', 'HEAD'])
# @pytest.mark.randomize(min_length=1, max_length=15, str_attrs=('digits', 'ascii_letters'), ncalls=3)
# def test_map_not_found(server, method, map_id: str):
#     header = {}
#     request = f'api/v1/maps/__{map_id}'
#     res = server.request(method, header, f'/{request}')
# 
#     assert res.status_code == 404
#     assert res.headers['content-type'] == 'application/json'
#     assert res.headers['cache-control'] == 'no-cache'
# 
#     if method != 'HEAD':
#         res_json = res.json()
# 
#         assert res_json['code'] == 'mapNotFound'
#         assert res_json.get('message')
#     else:
#         assert '' == res.text
# 
# 
# @pytest.mark.parametrize('method', ['GET', 'HEAD'])
# def test_map_success(server, method, map_dict):
#     map_dict.pop('dogSpeed', None)
#     header = {}
#     request = f'api/v1/maps/{map_dict["id"]}'
#     res = server.request(method, header, f'/{request}')
# 
#     assert res.status_code == 200
#     assert res.headers['content-type'] == 'application/json'
# 
#     if method != 'HEAD':
#         assert map_dict == res.json()
#     else:
#         assert '' == res.text


def test_list(server):
    request = 'api/v1/maps'
    res = server.get(f'/{request}')
    assert res.status_code == 200
    assert res.headers['content-type'] == 'application/json'
    assert res.json() == ans_list


def test_info(server):
    request = 'api/v1/maps/map1'
    res = server.get(f'/{request}')
    assert res.status_code == 200
    assert res.headers['content-type'] == 'application/json'
    assert res.json() == ans_info


def test_map_not_found(server):
    request = 'api/v1/maps/map33'
    res = server.get(f'/{request}')
    assert res.status_code == 404
    assert res.headers['content-type'] == 'application/json'
    assert res.json()["code"] == map_not_found["code"]


def test_bad_request(server):
    request = 'api/v333/maps/map1'
    res = server.get(f'/{request}')
    assert res.status_code == 400
    assert res.headers['content-type'] == 'application/json'
    assert res.json()["code"] == bad_request["code"]
