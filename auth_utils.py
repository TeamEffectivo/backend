from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import httpx
from jose import jwt
from EnvConfig import EnvConfig


security = HTTPBearer()

# Cognito Configuration from your EnvConfig
REGION = EnvConfig.AWS_REGION
USER_POOL_ID = EnvConfig.AWS_USER_POOL_ID
APP_CLIENT_ID = EnvConfig.AWS_APP_CLIENT_ID
JWKS_URL = f"https://cognito-idp.{REGION}.amazonaws.com/{USER_POOL_ID}/.well-known/jwks.json"

_cached_jwks = None

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    global _cached_jwks
    token = credentials.credentials
    
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
        return payload  # Returns user data (email, sub, etc.)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate credentials: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )