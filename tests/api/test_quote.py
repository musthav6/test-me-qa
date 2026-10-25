import pytest

from api.endpoints import line, quote
from helpers.catalog import find, in_stock, items_totaling, prices
from helpers.pricing import EXPRESS_SHIPPING, FREE_SHIPPING_FROM, STANDARD_SHIPPING, expected_quote

pytestmark = pytest.mark.api

COUPON = "WELCOME10"


def totals(resp):
    """Чотири суми розрахунку з відповіді /api/quote."""
    assert resp.status_code == 200, resp.text
    body = resp.json()
    return {key: body[key] for key in ("subtotal", "discount", "shipping", "total")}


@pytest.mark.parametrize("coupon", ["WELCOME10", "  WELCOME10  ", "welcome10", "Welcome10"])
def test_coupon_gives_10_percent_on_goods(api, catalog, coupon):
    items = [line(in_stock(catalog)["id"])]
    assert totals(quote(api, items, coupon=coupon)) == expected_quote(prices(catalog), items, coupon)


def test_unknown_coupon_returns_422(api, catalog):
    assert quote(api, [line(in_stock(catalog)["id"])], coupon="SALE50").status_code == 422


@pytest.mark.parametrize("amount, shipping", [
    pytest.param(FREE_SHIPPING_FROM - 100, STANDARD_SHIPPING, id="1 UAH below threshold"),
    pytest.param(FREE_SHIPPING_FROM, 0, id="exactly threshold"),
])
def test_standard_shipping_threshold(api, catalog, amount, shipping):
    items = items_totaling(catalog, amount)
    result = totals(quote(api, items))
    assert result["shipping"] == shipping
    assert result == expected_quote(prices(catalog), items)


def test_free_shipping_threshold_is_checked_before_discount(api, catalog):
    product = find(
        catalog,
        lambda p: p["stock"] > 0 and FREE_SHIPPING_FROM < p["price"] < FREE_SHIPPING_FROM * 10 // 9,
        "ціна вища за поріг, але нижча за нього після знижки 10%",
    )
    result = totals(quote(api, [line(product["id"])], coupon=COUPON))
    assert result["subtotal"] - result["discount"] < FREE_SHIPPING_FROM
    assert result["shipping"] == 0


@pytest.mark.parametrize("amount", [
    pytest.param(FREE_SHIPPING_FROM - 100, id="below threshold"),
    pytest.param(FREE_SHIPPING_FROM, id="exactly threshold"),
])
def test_express_shipping_is_always_150(api, catalog, amount):
    items = items_totaling(catalog, amount)
    assert totals(quote(api, items, delivery="express"))["shipping"] == EXPRESS_SHIPPING


def test_discount_does_not_apply_to_shipping(api, catalog):
    items = items_totaling(catalog, FREE_SHIPPING_FROM)
    result = totals(quote(api, items, coupon=COUPON, delivery="express"))
    assert result == expected_quote(prices(catalog), items, COUPON, "express")
    assert result["total"] == result["subtotal"] - result["discount"] + result["shipping"]


@pytest.mark.parametrize("quantity", [0, 11])
def test_quantity_out_of_range_returns_422(api, catalog, quantity):
    assert quote(api, [line(in_stock(catalog)["id"], quantity)]).status_code == 422
