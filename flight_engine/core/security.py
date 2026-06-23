from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from fastapi.security import OAuth2PasswordBearer
import jwt
from datetime import datetime, timedelta
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

SECRET_KEY = "my_super_secret_key"
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/token")

def create_access_token(data: dict, expires_delta: timedelta = timedelta(minutes=15)):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def verify_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return username
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession
from infrastructure.db import get_db_session

async def get_current_user_or_none(request: Request):
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload.get("sub")
        except:
            return None
    return None

async def check_anonymous_search_limit(
    request: Request,
    db: AsyncSession = Depends(get_db_session)
):
    user_id = await get_current_user_or_none(request)
    if user_id:
        return True # User is logged in, unlimited searches
        
    client_ip = request.client.host
    from sqlalchemy.future import select
    from infrastructure.models import AnonymousSearchTrackingModel
    
    result = await db.execute(select(AnonymousSearchTrackingModel).where(AnonymousSearchTrackingModel.ip_address == client_ip))
    tracker = result.scalars().first()
    
    if not tracker:
        tracker = AnonymousSearchTrackingModel(ip_address=client_ip, search_count=1)
        db.add(tracker)
        await db.commit()
    else:
        if tracker.search_count >= 10:
            raise HTTPException(status_code=403, detail="Limite de 10 buscas gratuitas excedido. Faça login para continuar.")
        tracker.search_count += 1
        await db.commit()
    
    return True
