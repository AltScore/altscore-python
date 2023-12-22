def build_headers(module):
    if isinstance(module.altscore_client.api_key, str):
        return {"API-KEY": module.altscore_client.api_key}
    elif isinstance(module.altscore_client.form_token, str):
        form_token = module.altscore_client.form_token.replace("Bearer ", "")
        return {"Authorization": f"Bearer {form_token}"}
    return {}
