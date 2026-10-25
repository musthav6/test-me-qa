import pytest

from api.endpoints import cancel_order, create_order, get_order, get_orders, line
from helpers.catalog import in_stock, limited_stock, out_of_stock, prices
from helpers.pricing import expected_quote

pytestmark = pytest.mark.api

COUPON = "WELCOME10"


def place_order(api, catalog, customer):
    """Успішне замовлення одного товару"""
    resp = create_order(api, [line(in_stock(catalog)["id"])], customer)
    assert resp.status_code == 201, resp.text
    return resp.json()


def order_ids(api, status="all"):
    resp = get_orders(api, status)
    assert resp.status_code == 200, resp.text
    return [order["id"] for order in resp.json()["items"]]


def test_approved_payment_creates_confirmed_order(api, catalog, customer):
    items = [line(in_stock(catalog)["id"])]
    resp = create_order(api, items, customer, coupon=COUPON)
    assert resp.status_code == 201, resp.text
    order = resp.json()
    assert order["status"] == "confirmed"
    expected = expected_quote(prices(catalog), items, COUPON)
    assert {key: order["totals"][key] for key in expected} == expected
    assert order_ids(api) == [order["id"]]


def test_declined_payment_returns_402_and_creates_nothing(api, catalog, customer):
    resp = create_order(api, [line(in_stock(catalog)["id"])], customer, payment="declined")
    assert resp.status_code == 402
    assert order_ids(api) == []


@pytest.mark.parametrize("field, value", [
    pytest.param("name", "Ян", id="name 2 chars"),
    pytest.param("name", "Я" * 80, id="name 80 chars"),
    pytest.param("name", "  Ян  ", id="name 2 chars after trim"),
    pytest.param("address", "Львів", id="address 5 chars"),
    pytest.param("address", "А" * 200, id="address 200 chars"),
])
def test_contact_boundaries_accepted(api, catalog, customer, field, value):
    customer[field] = value
    assert create_order(api, [line(in_stock(catalog)["id"])], customer).status_code == 201


@pytest.mark.parametrize("field, value", [
    pytest.param("name", "A", id="name 1 char"),
    pytest.param("name", "A ", id="name 1 char after trim"),
    pytest.param("name", "   ", id="name only spaces"),
    pytest.param("name", "Я" * 81, id="name 81 chars"),
    pytest.param("address", "  Київ  ", id="address 4 chars after trim"),
    pytest.param("address", "А" * 201, id="address 201 chars"),
    pytest.param("email", "not-an-email", id="email without @"),
])
def test_invalid_contacts_return_422(api, catalog, customer, field, value):
    customer[field] = value
    assert create_order(api, [line(in_stock(catalog)["id"])], customer).status_code == 422


def test_out_of_stock_product_cannot_be_ordered(api, catalog, customer):
    assert create_order(api, [line(out_of_stock(catalog)["id"])], customer).status_code == 409


def test_quantity_above_stock_returns_409(api, catalog, customer):
    product = limited_stock(catalog)
    assert create_order(api, [line(product["id"], product["stock"] + 1)], customer).status_code == 409


def test_order_details_show_items_and_totals(api, catalog, customer):
    order = place_order(api, catalog, customer)
    resp = get_order(api, order["id"])
    assert resp.status_code == 200
    details = resp.json()
    assert details["items"] == order["items"]
    assert details["totals"] == order["totals"]


def test_cancel_order(api, catalog, customer):
    order_id = place_order(api, catalog, customer)["id"]
    resp = cancel_order(api, order_id)
    assert resp.status_code == 200
    assert resp.json()["status"] == "cancelled"
    assert get_order(api, order_id).json()["status"] == "cancelled"


def test_repeated_cancel_returns_409(api, catalog, customer):
    order_id = place_order(api, catalog, customer)["id"]
    cancel_order(api, order_id)
    assert cancel_order(api, order_id).status_code == 409


def test_filter_orders_by_status(api, catalog, customer):
    kept = place_order(api, catalog, customer)["id"]
    cancelled = place_order(api, catalog, customer)["id"]
    cancel_order(api, cancelled)
    assert order_ids(api, "confirmed") == [kept]
    assert order_ids(api, "cancelled") == [cancelled]
    assert sorted(order_ids(api, "all")) == sorted([kept, cancelled])