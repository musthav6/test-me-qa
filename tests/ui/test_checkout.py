import pytest

from api.endpoints import get_orders, line
from helpers.catalog import find, in_stock, prices
from helpers.pricing import FREE_SHIPPING_FROM, expected_quote
from pages.orders_page import OrdersPage
from pages.shop_page import PAGE_SIZE

pytestmark = pytest.mark.ui

COUPON = "WELCOME10"


def server_order_ids(api):
    resp = get_orders(api)
    assert resp.status_code == 200, resp.text
    return [order["id"] for order in resp.json()["items"]]


def test_checkout_with_coupon_and_standard_delivery(shop, ui_api, catalog, customer):
    """TM-CHECKOUT-001"""
    product = find(catalog[:PAGE_SIZE], lambda p: p["stock"] > 0 and p["price"] >= FREE_SHIPPING_FROM,
                   "на першій сторінці, в наявності, від порогу безкоштовної доставки")
    items = [line(product["id"])]
    expected = expected_quote(prices(catalog), items, COUPON)

    # 1. «До кошика»: повідомлення і лічильник 1
    shop.add_to_cart(product["id"])
    shop.wait_toast("Товар додано до кошика")
    shop.wait_cart_count(1)

    # 2. Кошик: одна позиція, кількість 1, ціна товару
    cart = shop.open_cart()
    assert cart.lines() == [{**items[0], "price": product["price"]}]

    # 3. WELCOME10 і стандартна доставка: знижка 10%, доставка 0
    cart.apply_coupon(COUPON)
    assert cart.totals() == expected

    # 4. Контакти й успішна оплата: помилок немає, кнопка доступна
    cart.fill_contacts(customer)
    assert cart.error() == ""
    assert cart.can_place_order()

    # 5. Один клік: успіх, «Мої замовлення», рівно одне confirmed, кошик 0
    cart.place_order()
    shop.wait_toast("Замовлення успішно оформлено")
    cart.wait_closed()
    orders = OrdersPage(shop.driver).wait_open()
    [order] = orders.wait_orders(1)
    assert order["status"] == "confirmed"
    assert order["total"] == expected["total"]
    assert shop.cart_count() == 0
    assert server_order_ids(ui_api) == [order["id"]]

    # 6. Деталі: товар × 1, суми, номер замовлення
    details = orders.details(order["id"])
    assert details["number"] == order["id"]
    assert details["items"] == [f'{product["name"]} × 1']
    assert details["totals"] == {key: expected[key] for key in ("subtotal", "discount", "shipping")}

    # 7. Після reload: те саме замовлення без дубліката, кошик порожній
    shop.reload()
    assert OrdersPage(shop.driver).wait_open().wait_orders(1) == [order]
    assert shop.open_cart().lines() == []


def test_double_click_creates_single_order(shop, ui_api, catalog, customer):
    """TM-CHECKOUT-004"""
    shop.add_to_cart(in_stock(catalog[:PAGE_SIZE])["id"])
    shop.wait_cart_count(1)
    cart = shop.open_cart()
    cart.fill_contacts(customer)

    cart.double_click_place_order()
    shop.wait_toast("Замовлення успішно оформлено")
    [order] = OrdersPage(shop.driver).wait_open().wait_orders(1)
    assert server_order_ids(ui_api) == [order["id"]]
