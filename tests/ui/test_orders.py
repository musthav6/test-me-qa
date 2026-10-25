import pytest

from api.endpoints import cancel_order, create_order, line
from helpers.catalog import in_stock

pytestmark = pytest.mark.ui


@pytest.fixture
def placed_orders(ui_api, catalog, customer):
    """Два замовлення в середовищі браузера, створені через API: {"confirmed": id, "cancelled": id}."""
    ids = []
    for _ in range(2):
        resp = create_order(ui_api, [line(in_stock(catalog)["id"])], customer)
        assert resp.status_code == 201, resp.text
        ids.append(resp.json()["id"])
    assert cancel_order(ui_api, ids[1]).status_code == 200
    return {"confirmed": ids[0], "cancelled": ids[1]}


def unique_part(order_id, other_id, size=6):
    """Шматок із середини номера, якого немає в іншому номері: інакше пошук законно знайшов би обидва."""
    return next(order_id[i:i + size] for i in range(1, len(order_id) - size) if order_id[i:i + size] not in other_id)


def test_search_orders_by_part_of_number(shop, placed_orders):
    """TM-ORDERS-003"""
    page = shop.open_orders()
    page.wait_orders(2)

    page.search(unique_part(placed_orders["confirmed"], placed_orders["cancelled"]))
    assert [order["id"] for order in page.orders()] == [placed_orders["confirmed"]]


@pytest.mark.parametrize("status", ["confirmed", "cancelled", "all"])
def test_filter_orders_by_status(shop, placed_orders, status):
    """TM-ORDERS-002"""
    expected = set(placed_orders.values()) if status == "all" else {placed_orders[status]}
    page = shop.open_orders()
    page.wait_orders(2)

    page.filter_status(status)
    shown = page.orders()
    assert {order["id"] for order in shown} == expected
    assert len(shown) == len(expected)
