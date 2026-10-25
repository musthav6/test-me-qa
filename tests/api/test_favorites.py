import pytest

from api.endpoints import get_favorites, put_favorites

pytestmark = pytest.mark.api


@pytest.fixture
def product_ids(catalog):
    """Два різні товари з каталогу."""
    return [p["id"] for p in catalog[:2]]


def favorites(api):
    resp = get_favorites(api)
    assert resp.status_code == 200, resp.text
    return resp.json()["product_ids"]


def test_new_workspace_has_empty_favorites(api):
    assert favorites(api) == []


def test_favorites_are_saved_on_server(api, product_ids):
    assert put_favorites(api, product_ids).status_code == 200
    assert sorted(favorites(api)) == sorted(product_ids)


def test_favorites_have_no_duplicates(api, product_ids):
    first, second = product_ids
    put_favorites(api, [first, first, second])
    assert sorted(favorites(api)) == sorted(product_ids)


def test_remove_from_favorites(api, product_ids):
    first, second = product_ids
    put_favorites(api, [first, second])
    put_favorites(api, [second])
    assert favorites(api) == [second]
