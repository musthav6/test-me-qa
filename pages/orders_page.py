"""«Мої замовлення»: картки, деталі, пошук і фільтр за статусом."""
from selenium.webdriver.common.by import By

from pages.base_page import TOTALS_KEYS, BasePage, money

STATUSES = {"Підтверджено": "confirmed", "Скасовано": "cancelled"}
LOADING = "Завантажуємо замовлення"


class OrdersPage(BasePage):
    VIEW = (By.ID, "orders-view")
    LIST = (By.ID, "orders-list")
    CARD = (By.CSS_SELECTOR, '[data-testid="order-card"]')
    SEARCH = (By.ID, "order-search")
    STATUS_FILTER = (By.ID, "order-status")

    def wait_open(self):
        self.find(self.VIEW)
        self.wait_loaded()
        return self

    def wait_loaded(self):
        """Кожна зміна пошуку чи фільтра перезавантажує список; інших ознак завантаження, крім тексту, немає."""
        self.wait.until(lambda _: LOADING not in self.driver.find_element(*self.LIST).text)

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
        self.wait_loaded()

    def filter_status(self, status):
        self.select(self.STATUS_FILTER, status)
        self.wait_loaded()

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
