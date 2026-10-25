import pytest

pytestmark = pytest.mark.api

VALID_TEXT = "Чудові навушники, рекомендую!"


def post_review(client, rating=5, text=VALID_TEXT, product_id="p01"):
    return client.request("POST", f"/api/products/{product_id}/review", json={"rating": rating, "text": text})


def test_create_and_read_review(api):
    assert post_review(api).status_code == 201
    review = api.request("GET", "/api/products/p01/review").json()["review"]
    assert review["rating"] == 5
    assert review["text"] == VALID_TEXT


def test_no_review_in_new_workspace(api):
    assert api.request("GET", "/api/products/p01/review").json()["review"] is None


@pytest.mark.parametrize("rating", [1, 5])
def test_rating_boundaries_accepted(api, rating):
    assert post_review(api, rating=rating).status_code == 201


@pytest.mark.parametrize("rating", [0, 6])
def test_rating_out_of_range_rejected(api, rating):
    assert post_review(api, rating=rating).status_code == 422


@pytest.mark.parametrize("text, status", [
    ("а" * 9, 422),
    ("а" * 10, 201),
    ("а" * 500, 201),
    ("а" * 501, 422),
    ("   " + "а" * 9 + "   ", 422),  # 15 символів, але після trim лише 9
])
def test_text_length_after_trim(api, text, status):
    assert post_review(api, text=text).status_code == status


def test_second_review_on_same_product_returns_409(api):
    post_review(api)
    assert post_review(api, rating=3).status_code == 409


def test_html_is_stored_as_plain_text(api):
    # API зберігає текст як є; що він не виконується в браузері, перевіряє UI-тест
    payload = "<b>жирний</b> <img src=x onerror=alert(1)>"
    post_review(api, text=payload)
    assert api.request("GET", "/api/products/p01/review").json()["review"]["text"] == payload
