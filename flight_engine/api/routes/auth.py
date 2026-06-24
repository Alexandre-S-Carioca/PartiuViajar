from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from core.security import create_access_token
from core.config import settings
from infrastructure.db import get_db_session
from infrastructure.models import UserModel
from datetime import timedelta
import httpx
import json

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

@router.get("/google/login")
async def google_login():
    if not settings.GOOGLE_CLIENT_ID:
        # Mock flow se não houver chaves
        return RedirectResponse(url="/api/v1/auth/google/callback?code=mock_code_google")
    
    redirect_uri = f"{settings.SITE_URL}/api/v1/auth/google/callback"
    auth_url = f"https://accounts.google.com/o/oauth2/auth?response_type=code&client_id={settings.GOOGLE_CLIENT_ID}&redirect_uri={redirect_uri}&scope=openid%20profile%20email"
    return RedirectResponse(url=auth_url)

@router.get("/google/callback")
async def google_callback(code: str, db: AsyncSession = Depends(get_db_session)):
    if code == "mock_code_google" or not settings.GOOGLE_CLIENT_ID:
        user_info = {
            "email": "teste.google@gmail.com",
            "name": "Usuário Google de Teste",
            "picture": "https://ui-avatars.com/api/?name=Google&background=DB4437&color=fff",
            "sub": "google_123456"
        }
    else:
        # Real Google OAuth2 Token Exchange
        token_url = "https://oauth2.googleapis.com/token"
        redirect_uri = f"{settings.SITE_URL}/api/v1/auth/google/callback"
        data = {
            "code": code,
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code",
        }
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                token_response = await client.post(token_url, data=data)
                if token_response.status_code != 200:
                    raise HTTPException(status_code=400, detail=f"Failed to exchange token with Google: {token_response.text}")
                
                token_data = token_response.json()
                access_token = token_data.get("access_token")
                
                # Fetch User Info
                userinfo_url = "https://www.googleapis.com/oauth2/v3/userinfo"
                userinfo_response = await client.get(userinfo_url, headers={"Authorization": f"Bearer {access_token}"})
                if userinfo_response.status_code != 200:
                    raise HTTPException(status_code=400, detail="Failed to fetch user info from Google")
                    
                user_info = userinfo_response.json()
        except httpx.RequestError as exc:
            import logging
            logging.error(f"HTTPX error connecting to Google: {exc}")
            raise HTTPException(status_code=500, detail=f"Conexão com os servidores do Google falhou: {str(exc)}")
        except Exception as e:
            import logging
            logging.error(f"Unexpected error in Google Callback: {e}")
            raise HTTPException(status_code=500, detail=f"Erro inesperado no servidor: {str(e)}")

    return await _process_social_login(db, user_info, "google")

@router.get("/facebook/login")
async def facebook_login():
    if not settings.FACEBOOK_CLIENT_ID:
        return RedirectResponse(url="/api/v1/auth/facebook/callback?code=mock_code_facebook")
    
    redirect_uri = f"{settings.SITE_URL}/api/v1/auth/facebook/callback"
    auth_url = f"https://www.facebook.com/v12.0/dialog/oauth?client_id={settings.FACEBOOK_CLIENT_ID}&redirect_uri={redirect_uri}&scope=email,public_profile"
    return RedirectResponse(url=auth_url)

@router.get("/facebook/callback")
async def facebook_callback(code: str, db: AsyncSession = Depends(get_db_session)):
    if code == "mock_code_facebook" or not settings.FACEBOOK_CLIENT_ID:
        user_info = {
            "email": "teste.facebook@hotmail.com",
            "name": "Usuário Facebook de Teste",
            "picture": "https://ui-avatars.com/api/?name=Facebook&background=4267B2&color=fff",
            "sub": "fb_123456"
        }
    else:
        # Real Facebook OAuth2 Token Exchange
        token_url = "https://graph.facebook.com/v12.0/oauth/access_token"
        redirect_uri = f"{settings.SITE_URL}/api/v1/auth/facebook/callback"
        params = {
            "client_id": settings.FACEBOOK_CLIENT_ID,
            "redirect_uri": redirect_uri,
            "client_secret": settings.FACEBOOK_CLIENT_SECRET,
            "code": code,
        }
        async with httpx.AsyncClient() as client:
            token_response = await client.get(token_url, params=params)
            if token_response.status_code != 200:
                raise HTTPException(status_code=400, detail="Failed to exchange token with Facebook")
            
            token_data = token_response.json()
            access_token = token_data.get("access_token")
            
            # Fetch User Info
            userinfo_url = "https://graph.facebook.com/me?fields=id,name,email,picture.type(large)"
            userinfo_response = await client.get(userinfo_url, params={"access_token": access_token})
            if userinfo_response.status_code != 200:
                raise HTTPException(status_code=400, detail="Failed to fetch user info from Facebook")
                
            fb_data = userinfo_response.json()
            user_info = {
                "email": fb_data.get("email"),
                "name": fb_data.get("name"),
                "picture": fb_data.get("picture", {}).get("data", {}).get("url"),
                "sub": fb_data.get("id")
            }

    return await _process_social_login(db, user_info, "facebook")

async def _process_social_login(db: AsyncSession, user_info: dict, provider: str):
    email = user_info.get("email")
    if not email:
        raise HTTPException(status_code=400, detail="Email not provided by provider")

    # Verifica se usuario ja existe
    result = await db.execute(select(UserModel).where(UserModel.email == email))
    user = result.scalars().first()

    if not user:
        user = UserModel(
            email=email,
            name=user_info.get("name"),
            avatar_url=user_info.get("picture")
        )
        if provider == "google":
            user.google_id = user_info.get("sub")
        else:
            user.facebook_id = user_info.get("sub")
        db.add(user)
        await db.commit()
        await db.refresh(user)

    # Gera JWT
    access_token_expires = timedelta(days=7)
    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email, "name": user.name, "avatar": user.avatar_url},
        expires_delta=access_token_expires
    )
    
    # Redireciona devolta para o frontend com o token na URL (hash fragment ou querystring)
    # Na pratica pode ser um redirecionamento simples
    frontend_url = f"/?token={access_token}"
    return RedirectResponse(url=frontend_url)
