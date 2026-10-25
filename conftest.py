import allure
import pytest
from selenium import webdriver

from api.client import ApiClient
from helpers.catalog import load_catalog
from pages.shop_page import ShopPage


def pytest_addoption(parser):
    parser.addoption("--headed", action="store_true", help="Запуск браузера з вікном")


@pytest.hookimpl(wrapper=True)
def pytest_runtest_makereport(item, call):
    """Коли UI-тест падає, додаємо в Allure скріншот і адресу сторінки — доказ розбіжності."""
    report = yield
    driver = item.funcargs.get("driver")
    if report.failed and driver is not None:
        allure.attach(driver.get_screenshot_as_png(), "screenshot", allure.attachment_type.PNG)
        allure.attach(driver.current_url, "url", allure.attachment_type.URI_LIST)
    return report


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
def ui_api():
    """Середовище для браузера створює API-клієнт: він чекає Retry-After на 429, а магазин — ні."""
    return ApiClient(token=ApiClient().create_workspace())


@pytest.fixture
def shop(driver, ui_api):
    """Свіжий браузер із середовищем ui_api: UI і API бачать ті самі кошик, замовлення, відгуки."""
    return ShopPage(driver).open(ui_api.token)
