"""«Мої замовлення»: картки, деталі, пошук і фільтр за статусом."""
from selenium.webdriver.common.by import By

from pages.base_page import TOTALS_KEYS, BasePage, money

STATUSES = {"Підтверджено": "confirmed", "Скасовано": "cancelled"}


class OrdersPage(BasePage):
    VIEW = (By.ID, "orders-view")
    CARD = (By.CSS_SELECTOR, '[data-testid="order-card"]')
    SEARCH = (By.ID, "order-search")
    STATUS_FILTER = (By.ID, "order-status")

    def wait_open(self):
        self.find(self.VIEW)
        return self

    def orders(self):
        """Картки як словники. Повний id — з кнопки «Повторити»: вона є і в скасованих, а в заголовку лише короткий номер."""
        return [self._parse(card) for card in self.find_all(self.CARD)]

    def wait_orders(self, count):
        self.wait.until(lambda _: len(self.find_all(self.CARD)) == count)
        return self.orders()

    def details(self, order_id):
        """Розгортає «Деталі замовлення»: повний номер, рядки «Назва × N» і суми без «Разом»."""
        card = self._card(order_id)
        card.find_element(By.TAG_NAME, "summary").click()
        rows = [p.text for p in card.find_elements(By.CSS_SELECTOR, "details p")]
        totals = (part.split(":") for part in rows[-1].split("·"))
        return {
            "number": rows[0].split(":")[-1].strip(),
            "items": rows[1:-1],
            "totals": {TOTALS_KEYS[label.strip()]: money(value) for label, value in totals},
        }

    def search(self, text):
        self.type(self.SEARCH, text)

    def filter_status(self, status):
        self.select(self.STATUS_FILTER, status)

    def cancel(self, order_id):
        self.click((By.CSS_SELECTOR, f'[data-cancel="{order_id}"]'))

    def reorder(self, order_id):
        self.click((By.CSS_SELECTOR, f'[data-reorder="{order_id}"]'))

    def _card(self, order_id):
        return self.find((By.CSS_SELECTOR, f'[data-testid="order-card"]:has([data-reorder="{order_id}"])'))

    @staticmethod
    def _parse(card):
        order_id = card.find_element(By.CSS_SELECTOR, "[data-reorder]").get_attribute("data-reorder")
        header = card.find_element(By.TAG_NAME, "h3").text
        summary = card.find_element(By.CSS_SELECTOR, "header + p").text
        return {
            "id": order_id,
            "number": header.split("№")[-1].strip(),
            "status": STATUSES.get(card.find_element(By.CLASS_NAME, "status-pill").text),
            "total": money(summary.split("·")[-1]),
        }