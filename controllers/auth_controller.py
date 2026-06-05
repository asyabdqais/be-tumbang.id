from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from dependencies import get_db, get_current_user, create_access_token, create_refresh_token, verify_password, decode_token
from repositories.user_repository import get_user_by_username, create_user, get_users_by_role
from schemas.user_schema import UserCreate, UserResponse, UserAuth
from schemas.token_schema import Token, RefreshTokenRequest
from models.user_model import User, Role
import jwt

router = APIRouter()


@router.post("/register", response_model=UserResponse)
def register(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_user = get_user_by_username(db, username=user_data.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username sudah terdaftar")

    if user_data.role in [Role.DOKTER, Role.KADER, Role.ADMIN]:
        if current_user.role != Role.ADMIN:
            raise HTTPException(status_code=403, detail="Hanya Admin yang dapat membuat akun Dokter/Kader")

    if user_data.role == Role.ORANG_TUA:
        if current_user.role not in [Role.ADMIN, Role.KADER]:
            raise HTTPException(status_code=403, detail="Hanya Admin atau Kader yang dapat membuat akun Orang Tua")

    return create_user(db=db, user_data=user_data)


@router.post("/login", response_model=Token)
def login(form_data: UserAuth, db: Session = Depends(get_db)):
    """Login menggunakan JSON body — pure JWT, bukan OAuth2 form."""
    user = get_user_by_username(db, username=form_data.username)
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username atau password salah",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token  = create_access_token(data={"sub": user.username})
    refresh_token = create_refresh_token(data={"sub": user.username})
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.post("/refresh", response_model=Token)
def refresh_token(request: RefreshTokenRequest, db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token refresh tidak valid atau sudah kadaluarsa",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload  = decode_token(request.refresh_token)
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
    except jwt.InvalidTokenError:
        raise credentials_exception

    user = get_user_by_username(db, username=username)
    if user is None:
        raise credentials_exception

    access_token      = create_access_token(data={"sub": user.username})
    new_refresh_token = create_refresh_token(data={"sub": user.username})
    return {"access_token": access_token, "refresh_token": new_refresh_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.get("/users", response_model=List[UserResponse])
def list_users(
    role: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Daftar user, bisa difilter berdasarkan role."""
    role_enum = None
    if role:
        try:
            role_enum = Role(role)
        except ValueError:
            # Coba cocokkan case-insensitive
            for r in Role:
                if r.value.upper() == role.upper() or r.name.upper() == role.upper():
                    role_enum = r
                    break
            if role_enum is None:
                raise HTTPException(status_code=400, detail=f"Role '{role}' tidak valid")

    # Tentukan akses berdasarkan role user saat ini
    if current_user.role == Role.ADMIN:
        pass
    elif current_user.role == Role.KADER:
        if role_enum != Role.ORANG_TUA:
            raise HTTPException(status_code=403, detail="Kader hanya dapat melihat daftar user Orang Tua")
    else:
        raise HTTPException(status_code=403, detail="Hanya Admin yang dapat melihat daftar user")

    return get_users_by_role(db, role=role_enum)
