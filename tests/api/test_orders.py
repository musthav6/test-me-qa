import pytest

pytestmark = pytest.mark.api

CUSTOMER = {"name": "Олександр Тестовий", "email": "test@example.test", "address": "Київ, вул. Тестова, 12"}
SHCHODNIA = {"product_id": "p05", "quantity": 1}  # 500 грн, stock 20


def create_order(client, items=None, **overrides):
    payload = {"items": items or [SHCHODNIA], **CUSTOMER, **overrides}
    return client.request("POST", "/api/orders", json=payload)


def list_orders(client, status="all"):
    return client.request("GET", "/api/orders", params={"status": status}).json()["items"]


def test_approved_payment_creates_confirmed_order(api):
    resp = create_order(api, payment="approved")
    assert resp.status_code == 201
    order = resp.json()
    assert order["status"] == "confirmed"
    assert order["totals"]["total"] == 58000  # 500 + 80 доставка
    assert [o["id"] for o in list_orders(api)] == [order["id"]]


def test_declined_payment_returns_402_and_creates_nothing(api):
    assert create_order(api, payment="declined").status_code == 402
    assert list_orders(api) == []


@pytest.mark.parametrize("field, value", [
    ("name", "A"),
    ("name", "   "),
    ("name", "Я" * 81),
    ("address", "  Київ  "),
    ("email", "not-an-email"),
])
def test_invalid_contacts_return_422(api, field, value):
    assert create_order(api, **{field: value}).status_code == 422


@pytest.mark.xfail(strict=True, reason="BUG-009: ім'я з 1 символу після trim приймається")
def test_name_too_short_after_trim_returns_422(api):
    assert create_order(api, name="A ").status_code == 422


def test_out_of_stock_product_cannot_be_ordered(api):
    resp = create_order(api, items=[{"product_id": "p06", "quantity": 1}])  # stock 0
    assert resp.status_code == 409


def test_quantity_above_stock_returns_409(api):
    resp = create_order(api, items=[{"product_id": "p07", "quantity": 4}])  # «Фокус», stock 3
    assert resp.status_code == 409


def test_order_details(api):
    order_id = create_order(api).json()["id"]
    resp = api.request("GET", f"/api/orders/{order_id}")
    assert resp.status_code == 200
    order = resp.json()
    assert order["items"] == [SHCHODNIA]
    assert set(order["totals"]) >= {"subtotal", "discount", "shipping", "total"}


def test_cancel_order(api):
    order_id = create_order(api).json()["id"]
    resp = api.request("POST", f"/api/orders/{order_id}/cancel")
    assert resp.status_code == 200
    assert resp.json()["status"] == "cancelled"
    assert api.request("GET", f"/api/orders/{order_id}").json()["status"] == "cancelled"


@pytest.mark.xfail(strict=True, reason="BUG-010: повторне скасування повертає 200 замість 409")
def test_repeated_cancel_returns_409(api):
    order_id = create_order(api).json()["id"]
    api.request("POST", f"/api/orders/{order_id}/cancel")
    assert api.request("POST", f"/api/orders/{order_id}/cancel").status_code == 409


def test_filter_orders_by_status(api):
    kept = create_order(api).json()["id"]
    cancelled = create_order(api).json()["id"]
    api.request("POST", f"/api/orders/{cancelled}/cancel")
    assert [o["id"] for o in list_orders(api, "confirmed")] == [kept]
    assert [o["id"] for o in list_orders(api, "cancelled")] == [cancelled]
    assert len(list_orders(api, "all")) == 2
