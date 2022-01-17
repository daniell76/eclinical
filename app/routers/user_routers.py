# -*- encoding: utf-8 -*-
"""
    Copyright(C) 2021 Calyx
    All rights reserved

    File : user_routers.py
    Time : 2021/08/24 13:51:44
    Author : xiaf
    Version : 1.0
"""

from typing import List
from fastapi import APIRouter, Depends, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth.auths import Auth
from app.models.user_models import User, DBUser


router = APIRouter()


@router.get("/", response_model=List[User], response_model_exclude_unset=True)
async def read_all_users(request: Request, db: Session = Depends(get_db)):
    user = request.state.user
    db_users = DBUser.get_all_users(db)
    return db_users


@router.get("/me", response_model=User, response_model_exclude_unset=True)
async def read_user_me(request: Request):
    user = request.state.user
    return user


@router.get("/{username}", response_model=User, response_model_exclude_unset=True)
async def read_user_by_name(username: str, request: Request, db: Session = Depends(get_db)):
    my_user = request.state.user
    print(f"read_user_by_name: looking for {username}, requested by {my_user}.")
    user = DBUser.get_by_username(db, username)
    return user

# @router.post(
#   "/users/me/",
#   tags=["users"],
#   responses={403: {"description": "Operation forbidden"}}
#   )
# async def read_users_me(request: Request):
#     user = request.state.user
#     ret = trueReturn(data=User.from_orm(user).dict(exclude_unset=True), msg="My user info")
#     return ret
