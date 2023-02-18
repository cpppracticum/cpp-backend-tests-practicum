import re


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


def test_logs(docker_server):
    log_json = docker_server.get_log()
    pattern = '[Ss]erver (has )?started'
    search = re.search(pattern, log_json['message'])
    assert len(search.groups()) == 1
    assert log_json['data']['port'] == 8080
    assert log_json['data']['address'] == '0.0.0.0'
    request = 'images/cube.svg'
    res = docker_server.get(f'/{request}')
    log_json = docker_server.get_log()
    assert log_json['message'] == 'request received'
    assert log_json['data']['method'] == 'GET'
    assert log_json['data']['URI'] == '/images/cube.svg'
    log_json = docker_server.get_log()
    assert log_json['message'] == 'response sent'
    assert log_json['data']['code'] == 200
    assert log_json['data']['content_type'] == 'image/svg+xml'


def test_list(docker_server):
    request = 'api/v1/maps'
    res = docker_server.get(f'/{request}')
    assert res.status_code == 200
    assert res.headers['content-type'] == 'application/json'
    assert res.json() == ans_list


def test_info(docker_server):
    request = 'api/v1/maps/map1'
    res = docker_server.get(f'/{request}')
    assert res.status_code == 200
    assert res.headers['content-type'] == 'application/json'
    assert res.json() == ans_info


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


def test_image(docker_server):
    request = 'images/cube.svg'
    res = docker_server.get(f'/{request}')
    assert res.status_code == 200
    assert res.headers['content-type'] == 'image/svg+xml'


def test_file_not_found(docker_server):
    request = 'images/ccccube.svg'
    res = docker_server.get(f'/{request}')
    assert res.status_code == 404
    assert res.headers['content-type'] == 'text/plain'


def test_index_html(docker_server):
    request = 'index.html'
    res = docker_server.get(f'/{request}')
    assert res.status_code == 200
    assert res.headers['content-type'] == 'text/html'
    request2 = ''
    res2 = docker_server.get(f'/{request2}')
    assert res2.status_code == 200
    assert res2.headers['content-type'] == 'text/html'
    assert res2.text == res.text
