"""Спільне для всіх сторінок: очікування, суми з UI, token середовища."""
import json

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

from api.client import BASE_URL

STORAGE_KEY = "test-me:v2"
TIMEOUT = 10
TOTALS_KEYS = {"Товари": "subtotal", "Знижка": "discount", "Доставка": "shipping", "Разом": "total"}


def money(text):
    """в копійках: "1 234,56 грн" → 123456"""
    return int("".join(ch for ch in text if ch.isdigit()))


class BasePage:
    url = BASE_URL + "/"

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, TIMEOUT)

    def find(self, locator):
        return self.wait.until(EC.visibility_of_element_located(locator))

    def find_all(self, locator):
        return self.driver.find_elements(*locator)

    def click(self, locator):
        self.wait.until(EC.element_to_be_clickable(locator)).click()

    def type(self, locator, text):
        field = self.find(locator)
        field.clear()
        field.send_keys(text)

    def select(self, locator, value):
        Select(self.find(locator)).select_by_value(value)

    def wait_text(self, locator, text):
        """Чекаємо, поки в елементі з'явиться текст (тост, статус, лічильник)."""
        self.wait.until(EC.text_to_be_present_in_element(locator, text))

    def storage(self):
        """localStorage test-me:v2 = {token, cart, compare}."""
        raw = self.driver.execute_script("return localStorage.getItem(arguments[0])", STORAGE_KEY)
        return json.loads(raw) if raw else {}

    def token(self):
        """Token середовища, яке магазин створив у цьому браузері."""
        return self.wait.until(lambda _: self.storage().get("token"))

    def reload(self):
        self.driver.refresh()
