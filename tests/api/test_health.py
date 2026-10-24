import pytest


@pytest.mark.api
def test_health_ok(anon_api):
    resp = anon_api.request("GET", "/api/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"

