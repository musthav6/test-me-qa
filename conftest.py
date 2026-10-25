import pytest
from selenium import webdriver

from api.client import ApiClient
from helpers.catalog import load_catalog
from pages.shop_page import ShopPage


def pytest_addoption(parser):
    parser.addoption("--headed", action="store_true", help="Запуск браузера з вікном")


@pytest.fixture
def anon_api():
    return ApiClient()


@pytest.fixture
def api():
    return ApiClient(token=ApiClient().create_workspace())


@pytest.fixture
def other_api():
    """якщо треба два різні середовища для тестів, наприклад, щоб перевірити, що зміни в одному не впливають на інший"""
    return ApiClient(token=ApiClient().create_workspace())


@pytest.fixture(scope="session")
def catalog():
    """Каталог один раз завантажуємо"""
    return load_catalog(ApiClient())


@pytest.fixture
def customer():
    """тестовий юзер"""
    return {"name": "Денис Тестовий", "email": "test@example.test", "address": "Венеція, Юності 1"}


@pytest.fixture
def driver(request):
    options = webdriver.ChromeOptions()
    if not request.config.getoption("--headed"):
        options.add_argument("--headless=new")
    options.add_argument("--window-size=1400,900")
    drv = webdriver.Chrome(options=options)
    yield drv
    drv.quit()


@pytest.fixture
def shop(driver):
    """Свіжий браузер = нове середовище: магазин сам створює token."""
    return ShopPage(driver).open()


@pytest.fixture
def ui_api(shop):
    """API того самого середовища, що й браузер: готуємо дані й звіряємо результат."""
    return ApiClient(token=shop.token())
