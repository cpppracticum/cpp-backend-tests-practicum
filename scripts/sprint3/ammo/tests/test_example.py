

def test_ping(server):
    res = server.get('/ping')
    assert res.status_code == 200
    assert res.text == 'pong'


def test_pong(server):
    res = server.get('/pong')
    assert res.status_code == 200
    assert res.text == 'ping'


def test_hello(server):
    name = 'John'
    res = server.get(f'/hello/{name}')
    assert res.status_code == 200
    assert res.text == f'Hello {name}!'


def test_goodbye(server):
    name = 'John'
    res = server.get(f'/goodbye/{name}')
    assert res.status_code == 200
    assert res.text == f'Goodbye {name}!'
