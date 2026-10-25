import pytest

from api.endpoints import health

pytestmark = pytest.mark.api


def test_health_reports_version_and_dataset(anon_api):
    resp = health(anon_api)
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert body["version"]
    assert body["seed"]
