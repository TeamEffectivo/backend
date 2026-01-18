import httpx
from jose import jwt
from fastapi import HTTPException, status

from EnvConfig import EnvConfig

REGION = EnvConfig.AWS_REGION
USER_POOL_ID = EnvConfig.AWS_USER_POOL_ID
APP_CLIENT_ID = EnvConfig.AWS_APP_CLIENT_ID

JWKS_URL = f"https://cognito-idp.{REGION}.amazonaws.com/{USER_POOL_ID}/.well-known/jwks.json"

_cached_jwks = None

async def verify_cognito_token(token: str):
    global _cached_jwks
    try:
        if _cached_jwks is None:
            async with httpx.AsyncClient() as client:
                response = await client.get(JWKS_URL)
                _cached_jwks = response.json()

        payload = jwt.decode(
            token,
            _cached_jwks,
            algorithms=["RS256"],
            audience=APP_CLIENT_ID,
            issuer=f"https://cognito-idp.{REGION}.amazonaws.com/{USER_POOL_ID}"
        )
        return payload
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}"
        )