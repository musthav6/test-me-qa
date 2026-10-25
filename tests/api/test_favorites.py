import pytest

pytestmark = pytest.mark.api


def put_favorites(client, product_ids):
    return client.request("PUT", "/api/favorites", json={"product_ids": product_ids})


def get_favorites(client):
    return client.request("GET", "/api/favorites").json()["product_ids"]


def test_new_workspace_has_empty_favorites(api):
    assert get_favorites(api) == []


def test_favorites_are_saved_on_server(api):
    assert put_favorites(api, ["p01", "p02"]).status_code == 200
    assert sorted(get_favorites(api)) == ["p01", "p02"]


def test_favorites_have_no_duplicates(api):
    put_favorites(api, ["p01", "p01", "p02"])
    assert sorted(get_favorites(api)) == ["p01", "p02"]


def test_remove_from_favorites(api):
    put_favorites(api, ["p01", "p02"])
    put_favorites(api, ["p02"]) 
    assert get_favorites(api) == ["p02"]
