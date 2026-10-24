import pytest

ORBITA = {"product_id": "p01", "quantity": 1}  # 2 400 грн


@pytest.mark.api
def test_quote_with_welcome10(api):
    resp = api.request("POST", "/api/quote", json={"items": [ORBITA], "coupon": "WELCOME10"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["subtotal"] == 240000
    assert body["discount"] == 24000
    assert body["shipping"] == 0
    assert body["total"] == 216000


@pytest.mark.api
@pytest.mark.xfail(strict=True, reason="BUG-002: промокод чутливий до регістру")
def test_quote_coupon_case_insensitive(api):
    resp = api.request("POST", "/api/quote", json={"items": [ORBITA], "coupon": "welcome10"})
    assert resp.status_code == 200
    assert resp.json()["discount"] == 24000