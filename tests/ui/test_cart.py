import pytest

from api.endpoints import line
from helpers.catalog import in_stock, prices
from helpers.pricing import expected_quote
from pages.shop_page import PAGE_SIZE

pytestmark = pytest.mark.ui

COUPON = "WELCOME10"
ADDS = 3


def regular_product(catalog):
    return in_stock(catalog[:PAGE_SIZE])


def lowest_stock_product(catalog):
    """Найменший залишок, у який ще вміщаються ADDS штук: межа stock — ризикове місце."""
    return min((p for p in catalog if p["stock"] >= ADDS), key=lambda p: p["stock"])


@pytest.mark.parametrize("pick", [
    pytest.param(regular_product, id="regular product"),
    pytest.param(lowest_stock_product, id="lowest stock product"),
])
def test_adding_same_product_increases_quantity(shop, catalog, pick):
    """TM-CART-002"""
    product = pick(catalog)
    shop.go_to_product(product["id"])
    for _ in range(ADDS):
        shop.add_to_cart(product["id"])
    shop.wait_cart_count(ADDS)

    assert shop.open_cart().lines() == [{**line(product["id"], ADDS), "price": product["price"] * ADDS}]


def test_cart_and_coupon_survive_reload(shop, catalog):
    """TM-CART-007"""
    product = regular_product(catalog)
    items = [line(product["id"])]
    expected = expected_quote(prices(catalog), items, COUPON)

    shop.add_to_cart(product["id"])
    shop.wait_cart_count(1)
    cart = shop.open_cart()
    cart.apply_coupon(COUPON)
    assert cart.totals() == expected

    shop.reload()
    cart = shop.open_cart()
    assert cart.lines() == [{**items[0], "price": product["price"]}]
    assert cart.totals() == expected
