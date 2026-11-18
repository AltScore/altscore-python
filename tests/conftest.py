import httpx
import pytest


@pytest.fixture
def mock_http(monkeypatch):
    """Route every httpx.Client / httpx.AsyncClient created by the SDK to a handler.

    Usage: ``requests = mock_http(handler)`` where ``handler(request) -> httpx.Response``.
    The returned list collects every request that was sent.
    """
    original_client = httpx.Client
    original_async_client = httpx.AsyncClient

    def install(handler):
        sent = []

        def recording_handler(request):
            sent.append(request)
            return handler(request)

        transport = httpx.MockTransport(recording_handler)

        class Client(original_client):
            def __init__(self, *args, **kwargs):
                kwargs["transport"] = transport
                super().__init__(*args, **kwargs)

        class AsyncClient(original_async_client):
            def __init__(self, *args, **kwargs):
                kwargs["transport"] = transport
                super().__init__(*args, **kwargs)

        monkeypatch.setattr(httpx, "Client", Client)
        monkeypatch.setattr(httpx, "AsyncClient", AsyncClient)
        return sent

    return install
