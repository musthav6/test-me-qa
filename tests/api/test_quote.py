import pytest

pytestmark = pytest.mark.api

ORBITA = {"product_id": "p01", "quantity": 1}  # 2 400 грн
KHVYLIA = {"product_id": "p02", "quantity": 1}  # 1 500 грн, рівно поріг
DUGA = {"product_id": "p04", "quantity": 1}  # 999 грн
SHCHODNIA = {"product_id": "p05", "quantity": 1}  # 500 грн


def quote(client, items, coupon="", delivery="standard"):
    return client.request("POST", "/api/quote", json={"items": items, "coupon": coupon, "delivery": delivery})


def test_quote_with_welcome10(api):
    resp = quote(api, [ORBITA], coupon="WELCOME10")
    assert resp.status_code == 200
    body = resp.json()
    assert body["subtotal"] == 240000
    assert body["discount"] == 24000
    assert body["shipping"] == 0
    assert body["total"] == 216000


def test_coupon_ignores_outer_spaces(api):
    resp = quote(api, [ORBITA], coupon="  WELCOME10  ")
    assert resp.status_code == 200
    assert resp.json()["discount"] == 24000


@pytest.mark.xfail(strict=True, reason="BUG-002: промокод чутливий до регістру")
@pytest.mark.parametrize("coupon", ["welcome10", "Welcome10"])
def test_coupon_ignores_case(api, coupon):
    resp = quote(api, [ORBITA], coupon=coupon)
    assert resp.status_code == 200
    assert resp.json()["discount"] == 24000


def test_unknown_coupon_returns_422(api):
    assert quote(api, [ORBITA], coupon="SALE50").status_code == 422


def test_standard_shipping_below_threshold(api):
    body = quote(api, [DUGA, SHCHODNIA]).json()  
    assert body["subtotal"] == 149900
    assert body["shipping"] == 8000
    assert body["total"] == 157900


@pytest.mark.xfail(strict=True, reason="BUG-003: при сумі рівно 1 500 грн доставка не безкоштовна")
def test_free_shipping_from_exactly_1500(api):
    body = quote(api, [KHVYLIA]).json()
    assert body["shipping"] == 0
    assert body["total"] == 150000


def test_express_shipping_always_150(api):
    body = quote(api, [ORBITA], delivery="express").json()
    assert body["shipping"] == 15000
    assert body["total"] == 255000


def test_discount_does_not_apply_to_shipping(api):
    body = quote(api, [ORBITA], coupon="WELCOME10", delivery="express").json()
    assert body["discount"] == 24000  # 10% лише від товарів
    assert body["total"] == body["subtotal"] - body["discount"] + body["shipping"] == 231000


@pytest.mark.parametrize("quantity", [0, 11])
def test_quantity_out_of_range_returns_422(api, quantity):
    assert quote(api, [{"product_id": "p01", "quantity": quantity}]).status_code == 422
