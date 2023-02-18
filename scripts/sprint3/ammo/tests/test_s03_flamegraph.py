import os

from pathlib import Path

import pytest


@pytest.fixture
def directory():
    return Path(os.environ['DIRECTORY'])


def test_perf_data(directory):
    file = directory / 'perf.data'
    assert file.exists()
    assert file.stat().st_size


def test_graph(directory):
    file = directory / 'graph.svg'
    assert file.exists()
    assert file.stat().st_size
    content = file.read_text()
    assert content.count('http_handler::RequestHandler')
