import pytest
from selenium import webdriver

from api.client import ApiClient


def pytest_addoption(parser):
    parser.addoption("--headed", action="store_true", help="Запуск браузера з вікном")


@pytest.fixture
def anon_api():
    """Клієнт без token: каталог, health, перевірки 401."""
    return ApiClient()


@pytest.fixture
def api():
    """Клієнт із власним новим середовищем на кожен тест: тести незалежні й готові до xdist."""
    token = ApiClient().create_workspace()
    return ApiClient(token=token)


@pytest.fixture
def driver(request):
    options = webdriver.ChromeOptions()
    if not request.config.getoption("--headed"):
        options.add_argument("--headless=new")
    options.add_argument("--window-size=1400,900")
    drv = webdriver.Chrome(options=options)  # Selenium Manager сам знайде chromedriver
    yield drv
    drv.quit()
