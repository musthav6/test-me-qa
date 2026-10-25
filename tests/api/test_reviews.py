import pytest

from api.endpoints import get_review, post_review

pytestmark = pytest.mark.api

VALID_TEXT = "Тестовий відгук для перевірки API"


@pytest.fixture
def product_id(catalog):
    return catalog[0]["id"]


def test_new_workspace_has_no_review(api, product_id):
    resp = get_review(api, product_id)
    assert resp.status_code == 200
    assert resp.json()["review"] is None


def test_created_review_is_saved(api, product_id):
    assert post_review(api, product_id, 5, VALID_TEXT).status_code == 201
    review = get_review(api, product_id).json()["review"]
    assert review["rating"] == 5
    assert review["text"] == VALID_TEXT


@pytest.mark.parametrize("rating", [1, 5])
def test_rating_boundaries_accepted(api, product_id, rating):
    assert post_review(api, product_id, rating, VALID_TEXT).status_code == 201


@pytest.mark.parametrize("rating", [0, 6, 4.5])
def test_invalid_rating_returns_422(api, product_id, rating):
    assert post_review(api, product_id, rating, VALID_TEXT).status_code == 422


@pytest.mark.parametrize("text, status", [
    pytest.param("а" * 9, 422, id="9 chars"),
    pytest.param("а" * 10, 201, id="10 chars"),
    pytest.param("а" * 500, 201, id="500 chars"),
    pytest.param("а" * 501, 422, id="501 chars"),
    pytest.param("   " + "а" * 9 + "   ", 422, id="9 chars after trim"),
    pytest.param("   " + "а" * 10 + "   ", 201, id="10 chars after trim"),
    pytest.param("  " + "а" * 500 + "  ", 201, id="500 chars after trim"),
])
def test_text_length_after_trim(api, product_id, text, status):
    assert post_review(api, product_id, 5, text).status_code == status


def test_second_review_on_same_product_returns_409(api, product_id):
    assert post_review(api, product_id, 5, VALID_TEXT).status_code == 201
    assert post_review(api, product_id, 3, VALID_TEXT).status_code == 409


def test_html_is_stored_as_plain_text(api, product_id):
    # API зберігає текст як є; що HTML не виконується в браузері, перевіряє UI-тест
    text = "<b>жирний</b> <img src=x onerror=alert(1)>"
    assert post_review(api, product_id, 5, text).status_code == 201
    assert get_review(api, product_id).json()["review"]["text"] == text
