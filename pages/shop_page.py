"""Каталог і шапка магазину."""
from selenium.webdriver.common.by import By

from pages.base_page import BasePage
from pages.cart_dialog import CartDialog
from pages.orders_page import OrdersPage

PAGE_SIZE = 6  # ТЗ: по 6 товарів на сторінці


class ShopPage(BasePage):
    GRID = (By.CSS_SELECTOR, '[data-testid="product-grid"][aria-busy="false"]')
    CART_COUNT = (By.ID, "cart-count")
    CART_OPEN = (By.CSS_SELECTOR, '[data-testid="cart-open"]')
    TOAST = (By.ID, "toast")
    ORDERS_NAV = (By.CSS_SELECTOR, '[data-nav="orders"]')

    @staticmethod
    def add_button(product_id):
        return By.CSS_SELECTOR, f'.product-card [data-add="{product_id}"]'

    def open(self):
        """Відкриваємо магазин і чекаємо, поки завантажиться каталог і з'явиться token."""
        self.driver.get(self.url)
        self.find(self.GRID)
        self.token()
        return self

    def add_to_cart(self, product_id):
        self.click(self.add_button(product_id))

    def cart_count(self):
        return int(self.find(self.CART_COUNT).text)

    def wait_cart_count(self, count):
        """Точне число, а не «текст містить»: інакше «1» знайшлось би в «10»."""
        self.wait.until(lambda _: self.cart_count() == count)

    def wait_toast(self, text):
        self.wait_text(self.TOAST, text)

    def open_cart(self):
        self.click(self.CART_OPEN)
        return CartDialog(self.driver).wait_open()

    def open_orders(self):
        self.click(self.ORDERS_NAV)
        return OrdersPage(self.driver).wait_open()
