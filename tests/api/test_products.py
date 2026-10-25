import math

import pytest

from api.endpoints import get_product, get_products
from helpers.catalog import PAGE_LIMIT, out_of_stock, short_name

pytestmark = pytest.mark.api

CATEGORIES = ["Audio", "Workspace", "Lifestyle"]
PAGE_SIZE = 6  # ТЗ: по 6 товарів на сторінці


def found(client, **filters):
    """Товари, які повертає каталог з фільтрами."""
    resp = get_products(client, **filters)
    assert resp.status_code == 200, resp.text
    return resp.json()["items"]


def ids(products):
    return [p["id"] for p in products]


@pytest.mark.parametrize("transform", [
    pytest.param(lambda name: name, id="full name"),
    pytest.param(lambda name: name[:3], id="part of name"),
    pytest.param(lambda name: f"  {name}  ", id="outer spaces"),
    pytest.param(str.lower, id="lower case"),
    pytest.param(str.upper, id="upper case"),
])
def test_search_by_part_of_name(anon_api, catalog, transform):
    product = catalog[0]
    query = transform(short_name(product))
    result = found(anon_api, q=query, limit=PAGE_LIMIT)
    assert product["id"] in ids(result)
    assert all(query.strip().lower() in p["name"].lower() for p in result)


@pytest.mark.parametrize("category", CATEGORIES)
def test_category_filter(anon_api, catalog, category):
    result = found(anon_api, category=category, limit=PAGE_LIMIT)
    assert sorted(ids(result)) == sorted(p["id"] for p in catalog if p["category"] == category)


def test_price_bounds_are_inclusive(anon_api, catalog):
    price = catalog[0]["price"]
    result = found(anon_api, min_price=price, max_price=price, limit=PAGE_LIMIT)
    assert sorted(ids(result)) == sorted(p["id"] for p in catalog if p["price"] == price)


def test_min_price_greater_than_max_returns_422(anon_api, catalog):
    price = catalog[0]["price"]
    assert get_products(anon_api, min_price=price + 1, max_price=price).status_code == 422


def test_in_stock_excludes_zero_stock(anon_api, catalog):
    result = found(anon_api, in_stock="true", limit=PAGE_LIMIT)
    assert out_of_stock(catalog)["id"] not in ids(result)
    assert sorted(ids(result)) == sorted(p["id"] for p in catalog if p["stock"] > 0)


@pytest.mark.parametrize("sort, descending", [("price_asc", False), ("price_desc", True)])
def test_sort_by_price_is_numeric(anon_api, sort, descending):
    prices = [p["price"] for p in found(anon_api, sort=sort, limit=PAGE_LIMIT)]
    assert prices == sorted(prices, reverse=descending)


def test_filters_combine(anon_api, catalog):
    product = catalog[0]
    filters = {"category": product["category"], "in_stock": "true", "max_price": product["price"]}
    result = found(anon_api, **filters, sort="price_asc", limit=PAGE_LIMIT)
    expected = [p for p in catalog
                if p["category"] == filters["category"] and p["stock"] > 0 and p["price"] <= filters["max_price"]]
    assert sorted(ids(result)) == sorted(ids(expected))
    assert [p["price"] for p in result] == sorted(p["price"] for p in result)


def test_pages_have_6_products_without_overlaps(anon_api, catalog):
    page_count = math.ceil(len(catalog) / PAGE_SIZE)
    pages = [found(anon_api, page=n) for n in range(1, page_count + 1)]
    assert all(len(page) == PAGE_SIZE for page in pages[:-1])
    all_ids = [p for page in pages for p in ids(page)]
    assert sorted(all_ids) == sorted(ids(catalog))


@pytest.mark.parametrize("limit", [0, PAGE_LIMIT + 1])
def test_limit_out_of_range_returns_422(anon_api, limit):
    assert get_products(anon_api, limit=limit).status_code == 422


def test_product_details(anon_api, catalog):
    resp = get_product(anon_api, catalog[0]["id"])
    assert resp.status_code == 200
    product = resp.json()
    for field in ("name", "price", "stock", "description", "specs", "image"):
        assert field in product and product[field] not in ("", None, [], {}), field


def test_unknown_product_returns_404(anon_api):
    assert get_product(anon_api, "p999").status_code == 404