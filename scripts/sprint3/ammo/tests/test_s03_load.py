import os
import glob

from pathlib import Path

import pytest

import numpy as np


@pytest.fixture
def directory():
    return Path(os.environ['DIRECTORY'])


def test_only_200(directory):
    logdirname = max(glob.glob(os.path.join(directory, '*/')), key=os.path.getctime)
    filename = ''
    for file_name in os.listdir(logdirname):
        name, end = os.path.splitext(file_name)
        if name.startswith('phout_') and end == '.log':
            filename = file_name

    with open(os.path.join(logdirname, filename)) as phout:
        lines = phout.readlines()
        print(lines[:10])
        for line in lines:
            assert line.split()[-1] == '200'


def test_percentiles(directory):
    logdirname = max(glob.glob(os.path.join(directory, '*/')), key=os.path.getctime)
    filename = ''
    for file_name in os.listdir(logdirname):
        name, end = os.path.splitext(file_name)
        if name.startswith('phout_') and end == '.log':
            filename = file_name

    with open(os.path.join(logdirname, filename)) as phout:
        lines = phout.readlines()
        print(lines[:10])
        timings = []
        for line in lines:
            timings.append(float(line.split()[-10]))
        arr = np.array(timings)
        p50 = np.percentile(arr, 50)
        p90 = np.percentile(arr, 90)
        assert p50 <= 35000 # 35 ms == 35000 microseconds
        assert p90 <= 50000 # 50 ms == 50000 microseconds
