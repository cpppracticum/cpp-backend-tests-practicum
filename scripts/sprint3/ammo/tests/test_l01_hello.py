def test_hello(server):
    name = 'Baron'
    res = server.get(f'/{name}')
    assert res.status_code == 200
    assert res.text == f'Hello, {name}'
