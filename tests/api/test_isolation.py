import pytest

from api.client import ApiClient

pytestmark = pytest.mark.api

CHECKOUT = {
    "items": [{"product_id": "p05", "quantity": 1}],
    "name": "Олександр Тестовий",
    "email": "test@example.test",
    "address": "Київ, вул. Тестова, 12",
}


@pytest.fixture
def other_api():
    """Друге, незалежне середовище."""
    return ApiClient(token=ApiClient().create_workspace())


@pytest.mark.parametrize("method, path", [
    ("GET", "/api/favorites"),
    ("GET", "/api/orders"),
    ("POST", "/api/quote"),
    ("GET", "/api/products/p01/review"),
])
@pytest.mark.parametrize("token", [None, "invalid-token"])
def test_protected_endpoints_require_valid_token(method, path, token):
    client = ApiClient(token=token)
    kwargs = {"json": {"items": [{"product_id": "p01", "quantity": 1}]}} if method == "POST" else {}
    assert client.request(method, path, **kwargs).status_code == 401


def test_other_workspace_cannot_see_order(api, other_api):
    order_id = api.request("POST", "/api/orders", json=CHECKOUT).json()["id"]
    assert other_api.request("GET", f"/api/orders/{order_id}").status_code == 404
    assert other_api.request("POST", f"/api/orders/{order_id}/cancel").status_code == 404
    assert other_api.request("GET", "/api/orders").json()["items"] == []


def test_favorites_are_isolated(api, other_api):
    api.request("PUT", "/api/favorites", json={"product_ids": ["p01"]})
    assert other_api.request("GET", "/api/favorites").json()["product_ids"] == []


def test_reviews_are_isolated(api, other_api):
    api.request("POST", "/api/products/p01/review", json={"rating": 5, "text": "Відгук першого середовища"})
    assert other_api.request("GET", "/api/products/p01/review").json()["review"] is None
