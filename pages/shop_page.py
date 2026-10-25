"""Каталог і шапка магазину."""
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By

from pages.base_page import STORAGE_KEY, BasePage
from pages.cart_dialog import CartDialog
from pages.orders_page import OrdersPage
from pages.product_dialog import ProductDialog

PAGE_SIZE = 6  # ТЗ: по 6 товарів на сторінці


class ShopPage(BasePage):
    GRID = (By.CSS_SELECTOR, '[data-testid="product-grid"][aria-busy="false"]')
    CART_COUNT = (By.ID, "cart-count")
    CART_OPEN = (By.CSS_SELECTOR, '[data-testid="cart-open"]')
    TOAST = (By.ID, "toast")
    ORDERS_NAV = (By.CSS_SELECTOR, '[data-nav="orders"]')
    NEXT_PAGE = (By.ID, "next")
    PAGE_INFO = (By.ID, "page-info")
    WORKSPACE_STATUS = (By.ID, "workspace-status")

    @staticmethod
    def add_button(product_id):
        return By.CSS_SELECTOR, f'.product-card [data-add="{product_id}"]'

    def open(self, token):
        """Магазин стартує з готовим token: сам він створює середовище без повтору на 429 і зависає."""
        self.driver.get(self.url + "api/health")  # той самий origin, тож localStorage спільний із магазином
        self.driver.execute_script(
            "localStorage.setItem(arguments[0], JSON.stringify({token: arguments[1], cart: [], compare: []}))",
            STORAGE_KEY, token)
        self.driver.get(self.url)
        try:
            self.find(self.GRID)
        except TimeoutException:
            status = self.driver.find_element(*self.WORKSPACE_STATUS).text
            raise TimeoutException(f"Каталог не завантажився. Статус магазину: {status}") from None
        assert self.token() == token, "Магазин замінив token: UI і API працювали б з різними середовищами"
        return self

    def go_to_product(self, product_id):
        """Гортаємо «Далі →», поки картка товару не з'явиться на сторінці."""
        card = (By.CSS_SELECTOR, f'[data-testid="product-{product_id}"]')
        while not self.find_all(card):
            page = self.find(self.PAGE_INFO).text
            self.click(self.NEXT_PAGE)
            self.wait.until(lambda _: self.find(self.PAGE_INFO).text != page)
            self.find(self.GRID)

    def open_product(self, product_id):
        self.click((By.CSS_SELECTOR, f'.product-card .product-title[data-detail="{product_id}"]'))
        return ProductDialog(self.driver).wait_open()

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
