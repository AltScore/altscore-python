"""Public access links for store packages: create, list and revoke.

The links are meant to be opened from an AltScore front end: the public endpoints
require an Origin or Referer header on the altscore.ai domain (or localhost), so the
url printed here cannot be consumed with curl or from this SDK.
"""
from altscore import AltScore
from decouple import config

altscore = AltScore(
    client_id=config("ALTSCORE_CLIENT_ID"),
    client_secret=config("ALTSCORE_CLIENT_SECRET"),
    environment=config("ALTSCORE_ENVIRONMENT")
)
# %%
# Create a package to expose. Any existing package id works too.
borrower_id = config("ALTSCORE_SAMPLE_BORROWER_ID")
package_id = altscore.borrower_central.store_packages.create({
    "borrower_id": borrower_id,
    "alias": "public-link-sample",
    "label": "Public link sample",
    "content": {"hello": "world"},
    "content_type": "json"
})
package = altscore.borrower_central.store_packages.retrieve(package_id)
# %%
# Create a link valid for one day. Without ttl_seconds the backend defaults to 7 days.
public_link = package.create_public_link(ttl_seconds=24 * 60 * 60, purpose="download")
print(public_link.url, public_link.expires_at)
# %%
# The listing includes expired and revoked links, so check the flags.
public_links = package.get_public_links()
for public_access_token in public_links:
    print(
        public_access_token.id,
        public_access_token.purpose,
        public_access_token.expires_at,
        f"expired={public_access_token.is_expired}",
        f"revoked={public_access_token.is_revoked}"
    )
assert any(public_access_token.id == public_link.token for public_access_token in public_links)
# %%
# Revoking takes the token exactly as it was returned, 32 hex chars without dashes.
package.revoke_public_link(public_link.token)
revoked_link = next(
    public_access_token for public_access_token in package.get_public_links()
    if public_access_token.id == public_link.token
)
assert revoked_link.is_revoked
print("revoked at", revoked_link.revoked_at)
# %%
# The same three operations are available at the module level, taking the package id,
# which avoids the retrieve call above.
module_link = altscore.borrower_central.store_packages.create_public_link(
    package_id, ttl_seconds=24 * 60 * 60, purpose="download"
)
print(module_link.url, module_link.expires_at)
altscore.borrower_central.store_packages.revoke_public_link(module_link.token)
