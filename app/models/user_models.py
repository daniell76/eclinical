# -*- encoding: utf-8 -*-
"""
    Copyright(C) 2021 Calyx
    All rights reserved

    File : user_models.py
    Time : 2021/08/24 10:39:40
    Author : xiaf
    Version : 1.0
"""

from sqlalchemy import Column, DateTime, text
from sqlalchemy.dialects.mysql import INTEGER, VARCHAR, ENUM
from sqlalchemy.orm import Session
from app.database import Base
from pydantic import BaseModel
from typing import Optional


# Pydantic models
class User(BaseModel):
    id: Optional[int] = None
    username: str
    role: str
    login_time: Optional[int] = None
    active: bool = True

    class Config:
        orm_mode = True


# DB model
class DBUser(Base):
    __tablename__ = 'users'

    id = Column(INTEGER, primary_key=True, comment='User ID')
    username = Column(VARCHAR(100))
    password = Column(VARCHAR(100))
    gender = Column(VARCHAR(10), server_default=text("'M'"))
    role = Column(ENUM("USER", "ADMIN"), nullable=False, default="USER", comment='User Role')
    active = Column(INTEGER, server_default=text("'1'"))
    login_time = Column(INTEGER, server_default=text("'0'"), comment='login time, mainly for JWT verification')
    create_date = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    update_date = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))

    @classmethod
    def get_by_user_id(cls, db: Session, user_id):
        return cls.get_by_id(db, user_id)

    @classmethod
    def get_by_username(cls, db: Session, username):
        data = db.query(cls).filter_by(username=username).first()
        return data

    @classmethod
    def get_all_users(cls, db: Session):
        return [x for x in db.query(cls).all()]

    @classmethod
    def activate(cls, db: Session, username):
        db.query(cls).filter_by(username=username).update({cls.active: 1})
        db.commit()

    @classmethod
    def deactivate(cls, db: Session, username):
        db.query(cls).filter_by(username=username).update({cls.active: 0})
        db.commit()

    @classmethod
    def update_login_time(cls, db: Session, user_id, login_time):
        db.query(cls).filter_by(id=user_id).update({cls.login_time: login_time})
        db.commit()

    @classmethod
    def update_role(cls, db: Session, username, role):
        db.query(cls).filter_by(username=username).update({cls.role: role})
        db.commit()

    @classmethod
    def update_gender(cls, db: Session, username, gender):
        db.query(cls).filter_by(username=username).update({cls.gender: gender})
        db.commit()
