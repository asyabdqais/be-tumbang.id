import jwt
import datetime
from pwdlib import PasswordHash
from pwdlib.hashers.bcrypt import BcryptHasher
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from database import SessionLocal, SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS

# ─── Password Hashing ─────────────────────────────────────
pwd_context = PasswordHash((BcryptHasher(),))

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# ─── JWT Token ────────────────────────────────────────────
def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.datetime.now() + datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.datetime.now() + datetime.timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str) -> dict:
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

# ─── DB Session ───────────────────────────────────────────
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ─── JWT Bearer (pure, bukan OAuth2) ─────────────────────
bearer_scheme = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token tidak valid atau sudah kadaluarsa",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_token(credentials.credentials)
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except jwt.InvalidTokenError:
        raise credentials_exception

    from models.user_model import User
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    return user

# ─── Role Authorization (fungsi, bukan class OOP) ─────────
def require_roles(*allowed_roles):
    """
    Dependency factory non-OOP untuk pengecekan role.
    Contoh pemakaian: Depends(require_roles(Role.ADMIN, Role.KADER))
    """
    def role_checker(current_user=Depends(get_current_user)):
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Anda tidak memiliki izin untuk melakukan aksi ini"
            )
        return current_user
    return role_checker
