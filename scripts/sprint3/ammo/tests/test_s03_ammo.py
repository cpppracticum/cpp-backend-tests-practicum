import os
import glob

from pathlib import Path

import pytest


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
