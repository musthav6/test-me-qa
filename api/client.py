import os
import time

import requests

BASE_URL = os.getenv("BASE_URL", "https://test-me.vzl.one")


class ApiClient:
    """Тонка обгортка над requests: базова адреса, token середовища, повтор на 429."""

    def __init__(self, token=None, base_url=BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()
        # Cloudflare блокує стандартний User-Agent Python, тому задаємо свій
        self.session.headers["User-Agent"] = "test-me-qa/1.0"
        if token:
            self.session.headers["X-Workspace-Token"] = token

    def request(self, method, path, retries=3, **kwargs):
        for _ in range(retries):
            resp = self.session.request(method, self.base_url + path, timeout=20, **kwargs)
            if resp.status_code != 429:
                return resp
            time.sleep(int(resp.headers.get("Retry-After", "1")))
        return resp

    def create_workspace(self):
        resp = self.request("POST", "/api/workspaces")
        assert resp.status_code == 201, resp.text
        return resp.json()["token"]
