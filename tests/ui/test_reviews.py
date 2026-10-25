import pytest

from api.endpoints import get_review

pytestmark = pytest.mark.ui

# alert() заблокував би WebDriver, тому onerror ставить прапорець, який тест читає напряму
HTML_TEXT = '<b>жирний</b> <img src=x onerror="window.xss=1">'


def assert_shown_as_text(dialog):
    assert dialog.saved_review_text() == HTML_TEXT
    assert not dialog.review_has_markup()
    assert dialog.driver.execute_script("return window.xss") is None


def test_review_html_is_shown_as_text(shop, ui_api, catalog):
    """TM-REVIEW-002"""
    product_id = catalog[0]["id"]

    # 1. Залишити відгук з HTML: збережено на сервері як є
    dialog = shop.open_product(product_id)
    dialog.leave_review(4, HTML_TEXT)
    shop.wait_toast("Дякуємо за відгук!")
    resp = get_review(ui_api, product_id)
    assert resp.status_code == 200, resp.text
    assert resp.json()["review"]["text"] == HTML_TEXT

    # 2. Текст показано буквально, теги не розібрані, скрипт не виконався
    assert_shown_as_text(dialog)

    # Після reload відгук рендериться заново з відповіді API — перевіряємо ще раз
    shop.reload()
    assert_shown_as_text(shop.open_product(product_id))
