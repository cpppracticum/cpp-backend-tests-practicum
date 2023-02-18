import os
import json
import time
import subprocess

from pathlib import Path

import pytest


def test_report():
    report_path = Path(os.environ['REPORT_PATH'])
    report = json.loads(report_path.read_text())
    assert report['slowest_func_v0'] == 'addAnnotatedEdge'
    assert report['slowest_func_v1'] == 'getNode'
    assert report['slowest_func_v2']


@pytest.mark.parametrize('execution_number', range(10))
def test_time(execution_number):
    binary_path = os.environ['BINARY_PATH']
    arg = os.environ['ARG']
    proc = subprocess.Popen([binary_path, arg], shell=True)
    start = time.time()
    proc.wait()
    delta = time.time() - start
    assert delta < 0.1
