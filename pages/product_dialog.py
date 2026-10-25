"""Картка товару: деталі та відгук поточного середовища."""
from selenium.webdriver.common.by import By

from pages.base_page import BasePage


class ProductDialog(BasePage):
    DIALOG = (By.CSS_SELECTOR, "#product-dialog[open]")
    TITLE = (By.ID, "detail-title")
    RATING = (By.ID, "review-rating")
    TEXT = (By.ID, "review-text")
    SUBMIT = (By.CSS_SELECTOR, '#review-form [type="submit"]')
    SAVED_REVIEW = (By.CSS_SELECTOR, "#saved-review .review-card")
    SAVED_TEXT = (By.CSS_SELECTOR, "#saved-review .review-card p")
    MARKUP_IN_REVIEW = (By.CSS_SELECTOR, "#saved-review .review-card p *")

    def wait_open(self):
        self.find(self.DIALOG)
        self.find(self.TITLE)
        return self

    def leave_review(self, rating, text):
        self.select(self.RATING, str(rating))
        self.type(self.TEXT, text)
        self.click(self.SUBMIT)

    def saved_review_text(self):
        """Текст збереженого відгуку так, як його бачить користувач."""
        self.find(self.SAVED_REVIEW)
        return self.find(self.SAVED_TEXT).text

    def review_has_markup(self):
        """чи розібрав браузер текст як HTML: True — є тег всередині <p>."""
        return bool(self.find_all(self.MARKUP_IN_REVIEW))
