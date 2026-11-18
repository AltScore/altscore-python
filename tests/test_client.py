import jwt
import pytest

from altscore import AltScore, AltScoreAsync


@pytest.mark.parametrize("client_class", [AltScore, AltScoreAsync])
def test_api_key_client_does_not_log_in(client_class, mock_http):
    sent = mock_http(lambda request: pytest.fail(f"unexpected request {request.url}"))
    client = client_class(api_key="test-key")
    assert client.api_key == "test-key"
    assert sent == []


@pytest.mark.parametrize("environment, bc_url, cms_url", [
    ("production", "https://bc.altscore.ai", "https://api.altscore.ai"),
    ("sandbox", "https://bc.sandbox.altscore.ai", "https://api.sandbox.altscore.ai"),
])
def test_base_urls(environment, bc_url, cms_url):
    client = AltScore(api_key="k", environment=environment)
    assert client._borrower_central_base_url == bc_url
    assert client._cms_base_url == cms_url


def test_unknown_environment_raises():
    with pytest.raises(ValueError, match="Unknown environment"):
        AltScore(api_key="k", environment="nope")


def test_missing_credentials_raises():
    with pytest.raises(ValueError):
        AltScore()


def test_get_tenant_from_token():
    token = jwt.encode({"tenantId": "acme"}, "a-test-secret-that-is-at-least-32-bytes", algorithm="HS256")
    assert AltScore(user_token=token).get_tenant_from_token() == "acme"
