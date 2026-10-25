import pytest
from selenium import webdriver

from api.client import ApiClient


def pytest_addoption(parser):
    parser.addoption("--headed", action="store_true", help="Запуск браузера з вікном")


@pytest.fixture
def anon_api():
    return ApiClient()


@pytest.fixture
def api():
    token = ApiClient().create_workspace()
    return ApiClient(token=token)


@pytest.fixture
def driver(request):
    options = webdriver.ChromeOptions()
    if not request.config.getoption("--headed"):
        options.add_argument("--headless=new")
    options.add_argument("--window-size=1400,900")
    drv = webdriver.Chrome(options=options) 
    yield drv
    drv.quit()
