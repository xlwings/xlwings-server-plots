import os
from functools import lru_cache

import httpx
from fastapi import HTTPException, Security, status
from fastapi.security.api_key import APIKeyHeader
from pydantic import BaseModel

from .. import settings

# See: https://developers.google.com/identity/protocols/oauth2/openid-connect#discovery
GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"


class User(BaseModel):
    id: str
    email: str
    email_verified: bool
    domain: str


@lru_cache()
def get_google_userinfo_url():
    response = httpx.get(GOOGLE_DISCOVERY_URL)
    return response.json()["userinfo_endpoint"]


async def authenticate(
    token: str = Security(APIKeyHeader(name="Authorization")),
) -> User:
    # Anonymous user
    if settings.xlwings_api_key and settings.xlwings_api_key == token:
        return User(id="N/A", email="N/A", email_verified=False, domain="N/A")
    # Google User
    elif settings.google_allowed_domains and token.startswith("ya29"):
        # Decodes `ScriptApp.getOAuthToken()` from Apps Script (OAuth 2.0 access token)
        userinfo_url = get_google_userinfo_url()
        async with httpx.AsyncClient() as client:
            response = await client.get(
                userinfo_url, headers={"Authorization": f"Bearer {token}"}
            )
        if response.status_code == 200:
            userinfo = response.json()
            user = User(
                id=userinfo["sub"],
                email=userinfo["email"],
                email_verified=userinfo["email_verified"],
                domain=userinfo.get("hd")
                if userinfo.get("hd")
                else userinfo["email"].split("@")[1],
            )
            if user.domain in settings.google_allowed_domains and user.email_verified:
                return user
            else:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Unauthorized",
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid OAuth Token",
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
        )
