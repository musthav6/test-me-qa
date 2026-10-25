import pytest

from api.client import ApiClient
from api.endpoints import (cancel_order, create_order, get_favorites, get_order, get_orders, get_review, line,
                           post_review, put_favorites, quote)
from helpers.catalog import in_stock

pytestmark = pytest.mark.api

REVIEW_TEXT = "Відгук першого середовища"

# Кожен захищений ендпоінт із ТЗ: назва → (client, product_id) → Response
PROTECTED = {
    "GET favorites": lambda c, pid: get_favorites(c),
    "PUT favorites": lambda c, pid: put_favorites(c, [pid]),
    "GET review": lambda c, pid: get_review(c, pid),
    "POST review": lambda c, pid: post_review(c, pid, 5, REVIEW_TEXT),
    "POST quote": lambda c, pid: quote(c, [line(pid)]),
    "GET orders": lambda c, pid: get_orders(c),
}


@pytest.mark.parametrize("endpoint", PROTECTED)
@pytest.mark.parametrize("token", [None, "invalid-token"], ids=["no token", "invalid token"])
def test_protected_endpoints_require_valid_token(catalog, endpoint, token):
    call = PROTECTED[endpoint]
    assert call(ApiClient(token=token), in_stock(catalog)["id"]).status_code == 401


def test_other_workspace_cannot_access_order(api, other_api, catalog, customer):
    resp = create_order(api, [line(in_stock(catalog)["id"])], customer)
    assert resp.status_code == 201, resp.text
    order_id = resp.json()["id"]
    assert get_order(other_api, order_id).status_code == 404
    assert cancel_order(other_api, order_id).status_code == 404
    assert get_orders(other_api).json()["items"] == []


def test_favorites_are_isolated(api, other_api, catalog):
    assert put_favorites(api, [catalog[0]["id"]]).status_code == 200
    assert get_favorites(other_api).json()["product_ids"] == []


def test_reviews_are_isolated(api, other_api, catalog):
    product_id = catalog[0]["id"]
    assert post_review(api, product_id, 5, REVIEW_TEXT).status_code == 201
    assert get_review(other_api, product_id).json()["review"] is None
