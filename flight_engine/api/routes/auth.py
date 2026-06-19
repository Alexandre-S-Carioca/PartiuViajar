from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from core.security import create_access_token
from datetime import timedelta

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

@router.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    # Dummy login: aceita qualquer user/pass para gerar o token
    access_token_expires = timedelta(minutes=60)
    access_token = create_access_token(
        data={"sub": form_data.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
