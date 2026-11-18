import asyncio

import httpx
import pytest

from altscore.common import http_errors
from altscore.common.http_errors import raise_for_status_improved, retry_on_401, retry_on_401_async


def make_response(status_code, **kwargs):
    request = httpx.Request("GET", "https://bc.altscore.ai/v1/borrowers")
    return httpx.Response(status_code, request=request, **kwargs)


@pytest.fixture(autouse=True)
def no_backoff(monkeypatch):
    monkeypatch.setattr(http_errors, "BACKOFF_BASE_SECONDS", 0)


class FakeModule:
    def __init__(self, statuses):
        self.statuses = list(statuses)
        self.calls = 0
        self.renewals = 0

    def renew_token(self):
        self.renewals += 1

    def next_response(self):
        self.calls += 1
        raise_for_status_improved(make_response(self.statuses.pop(0), json={}))
        return "ok"


class SyncModule(FakeModule):
    @retry_on_401
    def call(self):
        return self.next_response()


class AsyncModule(FakeModule):
    @retry_on_401_async
    async def call(self):
        return self.next_response()


def test_success_does_not_raise():
    raise_for_status_improved(make_response(200, json={"ok": True}))


@pytest.mark.parametrize("status, label", [
    (404, "Client error"),
    (422, "Client error"),
    (500, "Server error"),
    (503, "Server error"),
])
def test_error_message_has_type_status_url_and_body(status, label):
    with pytest.raises(httpx.HTTPStatusError) as exc_info:
        raise_for_status_improved(make_response(status, json={"detail": "bad borrower"}))
    message = str(exc_info.value)
    assert message.startswith(f"{label} '{status} ")
    assert "https://bc.altscore.ai/v1/borrowers" in message
    assert "bad borrower" in message
    assert exc_info.value.response.status_code == status


def test_non_json_body_is_truncated():
    with pytest.raises(httpx.HTTPStatusError) as exc_info:
        raise_for_status_improved(make_response(500, text="x" * 1000))
    assert "x" * 200 in str(exc_info.value)
    assert "x" * 201 not in str(exc_info.value)


def test_sync_401_renews_token_once_and_retries():
    module = SyncModule([401, 200])
    assert module.call() == "ok"
    assert module.renewals == 1
    assert module.calls == 2


def test_sync_5xx_is_retried_then_succeeds():
    module = SyncModule([500, 502, 200])
    assert module.call() == "ok"
    assert module.calls == 3
    assert module.renewals == 0


def test_sync_5xx_gives_up_after_max_retries():
    module = SyncModule([500] * (1 + http_errors.MAX_RETRIES_ON_5XX))
    with pytest.raises(httpx.HTTPStatusError):
        module.call()
    assert module.calls == 1 + http_errors.MAX_RETRIES_ON_5XX


def test_sync_4xx_is_not_retried():
    module = SyncModule([404, 200])
    with pytest.raises(httpx.HTTPStatusError):
        module.call()
    assert module.calls == 1


def test_async_401_renews_token_once_and_retries():
    module = AsyncModule([401, 200])
    assert asyncio.run(module.call()) == "ok"
    assert module.renewals == 1


def test_async_5xx_gives_up_after_max_retries():
    module = AsyncModule([503] * (1 + http_errors.MAX_RETRIES_ON_5XX))
    with pytest.raises(httpx.HTTPStatusError):
        asyncio.run(module.call())
    assert module.calls == 1 + http_errors.MAX_RETRIES_ON_5XX
