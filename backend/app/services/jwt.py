from datetime import datetime, timedelta, UTC
import jwt
from app.core.config import settings
from app.repositories.token import tokenCRUD


class TokenFunctionality:
    @staticmethod
    def create_access_token(user_id: str) -> str:
        payload = {
            "sub": user_id,
            "type": "access",
            "exp": datetime.now(UTC) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        }
        return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    @staticmethod
    def decode_token(token: str) -> dict:
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            raise
        except jwt.InvalidTokenError:
            raise

    @staticmethod
    async def ensure_valid_access_token(access_token: str, session) -> dict:
        try:
            payload = TokenFunctionality.decode_token(access_token)
            if payload.get("type") != "access":
                return {"status": "login_required"}
            return {"status": "valid", "payload": payload}
        except jwt.ExpiredSignatureError:
            try:
                payload = jwt.decode(
                    access_token,
                    settings.SECRET_KEY,
                    algorithms=[settings.ALGORITHM],
                    options={"verify_exp": False},
                )
            except jwt.InvalidTokenError:
                raise
        
            user_id = payload.get("sub")
            if not user_id:
                return {"status": "login_required"}

            try:
                has_refresh = await tokenCRUD.token_exists(user_id, session)
            except Exception:
                return {"status": "login_required"}

            if has_refresh:
                return {"status": "refresh_required"}
            return {"status": "login_required"}
        except jwt.InvalidTokenError:
            raise


    @staticmethod
    async def create_refresh_token(user_id: str, session) -> str:
        existing = await tokenCRUD.get_valid_refresh_token(user_id, session)
        expire_time = datetime.now(UTC) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

        if existing:
            await tokenCRUD.delete_refresh_token(user_id,session)


        payload = {
            "sub": str(user_id),
            "type": "refresh",
            "exp": expire_time,
        }
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        await tokenCRUD.add_token(token, user_id, expire_time, session)
        return token

    @staticmethod
    async def delete_token(user_id: str, session) -> dict:
        try:
            has_refresh = await tokenCRUD.token_exists(user_id, session)
        except Exception:
            return {"status": "already logged out"}
        if has_refresh:
            await tokenCRUD.delete_refresh_token(user_id, session)
            return {"status": "Logged out successfully"}
        return {"status": "already logged out"}

    @staticmethod
    async def refresh_token(token: str, session) -> dict:
        try:
            decoded_token = TokenFunctionality.decode_token(token)
        except jwt.PyJWTError:
            return {"status": "login_required"}

        user_id = decoded_token["sub"]
        flag = await tokenCRUD.token_exists(user_id, session)
        if flag:
            access_token = TokenFunctionality.create_access_token(user_id)
            return {"access_token": access_token, "refresh_token": token, "token_type": "bearer"}
        return {"status": "login_required"}
