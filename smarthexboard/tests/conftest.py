import pytest

from smarthexboard.smarthexboardlib.utils.plugin import Tests


@pytest.hookimpl
def pytest_sessionstart(session):
    # print("Test session is starting")
    Tests.are_running = True


@pytest.hookimpl
def pytest_sessionfinish(session):
    # print("Test session is ending")
    Tests.are_running = False
