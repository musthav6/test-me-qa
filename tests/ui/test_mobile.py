import pytest

from api.endpoints import get_orders
from helpers.catalog import in_stock
from pages.base_page import MOBILE_WIDTH
from pages.orders_page import OrdersPage
from pages.shop_page import PAGE_SIZE

pytestmark = [pytest.mark.ui, pytest.mark.mobile]


def assert_fits_screen(page, screen):
    overflow = page.horizontal_overflow()
    assert overflow <= 0, f"{screen}: вміст ширший за екран на {overflow}px, з'являється горизонтальний скрол"


def test_purchase_on_360px_without_horizontal_scroll(shop, ui_api, catalog, customer):
    """TM-MOBILE-001"""
    assert shop.viewport_width() == MOBILE_WIDTH
    assert_fits_screen(shop, "Каталог")

    product = in_stock(catalog[:PAGE_SIZE])
    shop.add_to_cart(product["id"])
    shop.wait_cart_count(1)
    cart = shop.open_cart()
    assert_fits_screen(cart, "Кошик")

    cart.fill_contacts(customer)
    cart.place_order()
    shop.wait_toast("Замовлення успішно оформлено")
    orders = OrdersPage(shop.driver).wait_open()
    [order] = orders.wait_orders(1)
    assert_fits_screen(orders, "Мої замовлення")

    resp = get_orders(ui_api)
    assert resp.status_code == 200, resp.text
    assert [o["id"] for o in resp.json()["items"]] == [order["id"]]
