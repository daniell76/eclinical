# -*- encoding: utf-8 -*-
"""
    Copyright(C) 2021 Calyx
    All rights reserved

    File : auth_routers.py
    Time : 2021/08/24 13:51:44
    Author : xiaf
    Version : 1.0
"""

from fastapi import APIRouter, Depends, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth.auths import Auth
from app.models.user_models import User, DBUser

router = APIRouter()


@router.post("/register", response_model=User)
async def register(request: Request, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Register a new user"""
    # hash the clear text password
    password = Auth.get_password_hash(form_data.password)

    db_user = DBUser.get_by_username(db, form_data.username)

    if db_user:
        return db_user

    # Username "All" is not allowed
    if form_data.username.lower() == "all":
        active = False
    else:
        active = True

    db_user = DBUser(username=form_data.username, password=password, active=active)

    DBUser.add(db, db_user)
    db.commit()

    # request.session['test'] = "test"
    # print(request.session)

    return db_user


@router.post("/login")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    res = Auth.login_authenticate(form_data.username, form_data.password, db)
    return res
