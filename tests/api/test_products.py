import pytest

pytestmark = pytest.mark.api


def get_products(client, **params):
    resp = client.request("GET", "/api/products", params=params)
    assert resp.status_code == 200, resp.text
    return resp.json()


def ids(body):
    return [p["id"] for p in body["items"]]


@pytest.mark.parametrize("query", ["Хвиля", "  Хвиля  ", "Хви"])
def test_search_by_part_of_name(anon_api, query):
    assert ids(get_products(anon_api, q=query)) == ["p02"]


@pytest.mark.xfail(strict=True, reason="BUG-008: пошук чутливий до регістру")
@pytest.mark.parametrize("query", ["хвиля", "ХВИЛЯ"])
def test_search_ignores_case(anon_api, query):
    assert ids(get_products(anon_api, q=query)) == ["p02"]


def test_category_filter(anon_api):
    body = get_products(anon_api, category="Audio", limit=20)
    assert body["items"]
    assert {p["category"] for p in body["items"]} == {"Audio"}


def test_price_bounds_are_inclusive(anon_api):
    # p02 коштує рівно 150000: має потрапити і під min, і під max
    body = get_products(anon_api, min_price=150000, max_price=150000, limit=20)
    assert "p02" in ids(body)
    assert all(p["price"] == 150000 for p in body["items"])


def test_min_price_greater_than_max_is_rejected(anon_api):
    resp = anon_api.request("GET", "/api/products", params={"min_price": 200000, "max_price": 100000})
    assert resp.status_code == 422


def test_in_stock_excludes_zero_stock(anon_api):
    body = get_products(anon_api, in_stock="true", limit=20)
    assert "p06" not in ids(body)  # «Мандрівник», stock 0
    assert all(p["stock"] > 0 for p in body["items"])


@pytest.mark.parametrize("sort, reverse", [("price_asc", False), ("price_desc", True)])
def test_sort_by_price_is_numeric(anon_api, sort, reverse):
    prices = [p["price"] for p in get_products(anon_api, sort=sort, limit=20)["items"]]
    assert prices == sorted(prices, reverse=reverse)


def test_filters_combine(anon_api):
    body = get_products(anon_api, category="Audio", in_stock="true", sort="price_asc", max_price=200000, limit=20)
    prices = [p["price"] for p in body["items"]]
    assert all(p["category"] == "Audio" and p["stock"] > 0 and p["price"] <= 200000 for p in body["items"])
    assert prices == sorted(prices)


def test_pagination_has_no_overlaps(anon_api):
    page1 = ids(get_products(anon_api, page=1, limit=6))
    page2 = ids(get_products(anon_api, page=2, limit=6))
    assert len(page1) == 6
    assert not set(page1) & set(page2)


def test_product_details(anon_api):
    resp = anon_api.request("GET", "/api/products/p01")
    assert resp.status_code == 200
    product = resp.json()
    for field in ("name", "price", "stock", "description", "specs", "image"):
        assert product.get(field), field


def test_unknown_product_returns_404(anon_api):
    assert anon_api.request("GET", "/api/products/p999").status_code == 404
