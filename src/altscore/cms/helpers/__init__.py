from typing import Optional


def build_headers(module, partner_id: Optional[str] = None):
    headers = {}
    if isinstance(module.altscore_client.api_key, str):
        headers["X-API-KEY"] = module.altscore_client.api_key
    elif isinstance(module.altscore_client.user_token, str):
        user_token = module.altscore_client.user_token.replace("Bearer ", "")
        headers["Authorization"] = f"Bearer {user_token}"
    if isinstance(partner_id, str):
        headers["X-PARTNER-ID"] = partner_id
    return headers
