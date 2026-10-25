"""Діалог кошика: позиції, промокод, доставка, підсумки й оформлення."""
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from pages.base_page import TOTALS_KEYS, BasePage, money


class CartDialog(BasePage):
    DIALOG = (By.CSS_SELECTOR, "#bag-dialog[open]")
    LINE = (By.CSS_SELECTOR, "#bag-items [data-cart-line]")
    QUANTITY = (By.CSS_SELECTOR, '[data-testid^="quantity-"]')
    PRICE = (By.CSS_SELECTOR, ".price")
    COUPON = (By.CSS_SELECTOR, '[data-testid="coupon"]')
    APPLY_COUPON = (By.ID, "apply-coupon")
    DELIVERY = (By.ID, "delivery")
    TOTALS_ROW = (By.CSS_SELECTOR, "#totals > div")
    NAME = (By.ID, "customer-name")
    EMAIL = (By.ID, "email")
    ADDRESS = (By.ID, "address")
    PAYMENT = (By.ID, "payment")
    ERROR = (By.ID, "checkout-error")
    PLACE_ORDER = (By.CSS_SELECTOR, '[data-testid="place-order"]')

    def wait_open(self):
        self.find(self.DIALOG)
        self.wait_recalculated()
        return self

    def wait_recalculated(self):
        """Поки йде перерахунок, кнопка оформлення disabled. Готово: кнопка активна або є помилка."""
        def done(_):
            button = self.driver.find_element(*self.PLACE_ORDER)
            return button.is_enabled() or self.error()
        self.wait.until(done)

    def lines(self):
        """[{product_id, quantity, price}] у порядку відображення; price — сума рядка в копійках."""
        result = []
        for row in self.find_all(self.LINE):
            quantity = row.find_element(*self.QUANTITY)
            result.append({
                "product_id": quantity.get_attribute("data-testid").removeprefix("quantity-"),
                "quantity": int(quantity.text),
                "price": money(row.find_element(*self.PRICE).text),
            })
        return result

    def apply_coupon(self, code):
        self.type(self.COUPON, code)
        self.click(self.APPLY_COUPON)
        self.wait_recalculated()

    def choose_delivery(self, delivery):
        self.select(self.DELIVERY, delivery)
        self.wait_recalculated()

    def totals(self):
        """{subtotal, discount, shipping, total} у копійках — порівнюється з expected_quote напряму."""
        result = {}
        for row in self.find_all(self.TOTALS_ROW):
            label, value = row.find_elements(By.TAG_NAME, "span")
            result[TOTALS_KEYS[label.text]] = money(value.text)
        return result

    def fill_contacts(self, customer, payment="approved"):
        self.type(self.NAME, customer["name"])
        self.type(self.EMAIL, customer["email"])
        self.type(self.ADDRESS, customer["address"])
        self.select(self.PAYMENT, payment)

    def can_place_order(self):
        return self.driver.find_element(*self.PLACE_ORDER).is_enabled()

    def place_order(self):
        self.click(self.PLACE_ORDER)

    def error(self):
        return self.driver.find_element(*self.ERROR).text

    def wait_closed(self):
        self.wait.until(EC.invisibility_of_element_located(self.DIALOG))