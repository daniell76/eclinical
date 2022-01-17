# -*- encoding: utf-8 -*-
"""
    Copyright(C) 2021 Calyx
    All rights reserved

    File : database.py
    Time : 2020/08/01 20:21:48
    Author : xiaf
    Version : 1.0
"""
from typing import Dict

from sqlalchemy import create_engine, desc, distinct
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.functions import func
# from sqlalchemy.dialects import mysql
from app.config import get_config


class CommonTable:
    """
    Base for all table classes
    """
    @classmethod
    def add(cls, db: Session, data):
        db.add(data)

    @classmethod
    def get_all(cls, db: Session, filter_by: Dict = None, page_num: int = 1, page_size: int = 0, reverse: bool = False):
        if page_size <= 0:
            # no need to page
            if filter_by is None:
                query = db.query(cls)
                # data = db.query(cls).all()
            else:
                query = db.query(cls).filter_by(**filter_by)
                # data = db.query(cls).filter_by(**filter_by).all()
            if reverse:
                query = query.order_by(desc(cls.update_date))
        else:
            if page_num <= 1:
                page_num = 1
            if filter_by is None:
                # totalPages = db.execute(
                #     db.query(cls).statement.with_only_columns(
                #         [func.count(cls.id)]
                #     ).order_by(None)
                # ).scalar()
                offset = page_size * (page_num - 1)
                query = db.query(cls)
                if reverse:
                    query = query.order_by(desc(cls.update_date))
                query = query.limit(page_size).offset(offset)
                # data = db.query(cls).limit(page_size).offset(offset).all()
            else:
                # totalPages = db.execute(
                #     db.query(cls).filter_by(**filter_by).statement.with_only_columns(
                #         [func.count(cls.id)]
                #     ).order_by(None)
                # ).scalar()
                offset = page_size * (page_num - 1)
                query = db.query(cls).filter_by(**filter_by)
                if reverse:
                    query = query.order_by(desc(cls.update_date))
                query = query.limit(page_size).offset(offset)
                # data = db.query(cls).filter_by(**filter_by).limit(page_size).offset(offset).all()
        # print(f'********{str(query.statement.compile(dialect=mysql.dialect()))}')
        # print(f'********{str(query.statement.compile(compile_kwargs = {"literal_binds": True}))}')
        # data = query.all()
        # print(data, type(data))
        # print([dict(x) for x in data])
        # return [x for x in data]
        return query.all()

    @classmethod
    def count_all(cls, db: Session, filter_by: Dict = None) -> int:
        if filter_by is None:
            return db.query(func.count(cls.id)).scalar()
        else:
            return db.query(func.count(cls.id)).filter_by(**filter_by).scalar()

    @classmethod
    def count_all_with_condition(cls, db: Session, filter_statement: str = None) -> int:
        if filter_statement is None:
            return db.query(func.count(cls.id)).scalar()
        else:
            return db.query(func.count(cls.id)).filter(filter_statement).scalar()

    @classmethod
    def get_by_id(cls, db: Session, row_id: int):
        data = db.query(cls).filter_by(id=row_id).first()
        return data

    @classmethod
    def get_by_project_id(cls, db: Session, uuid: str):
        data = db.query(cls).filter_by(uuid=uuid).all()
        return [x for x in data]

    @classmethod
    def get_by_project_version(cls, db: Session, uuid: str, version: int):
        data = db.query(cls).filter((cls.uuid == uuid) & (cls.version == version)).all()
        return [x for x in data]

    @classmethod
    def update_by_id(cls, db: Session, row_id: int, **kwargs):
        db.query(cls).filter_by(id=row_id).update(kwargs)
        data = db.query(cls).filter_by(id=row_id).first()
        return data

    @classmethod
    def delete_by_id(cls, db: Session, row_id: int):
        db.query(cls).filter_by(id=row_id).delete()

    @classmethod
    def delete_by_project_id(cls, db: Session, uuid: str):
        db.query(cls).filter_by(uuid=uuid).delete()

    @classmethod
    def delete_by_project_version(cls, db: Session, uuid: str, version: int):
        db.query(cls).filter((cls.uuid == uuid) & (cls.version == version)).delete()

    @classmethod
    def get_max_version(cls, db: Session, uuid: str) -> int:
        sql = f'''
            SELECT IFNULL(MAX(`version`), 0) version FROM {cls.__tablename__} WHERE `uuid`='{uuid}';
        '''
        res = db.execute(sql).first()
        return res.version

    @classmethod
    def get_versions(cls, db: Session, uuid: str):
        q = db.query(distinct(cls.version), cls.update_date).filter_by(uuid=uuid).order_by(desc(cls.update_date))
        # q = db.query(distinct(cls.version), func.max(cls.update_date).label("update_date")
        #              ).filter_by(uuid=uuid).order_by(desc(cls.update_date))
        # print(f'********{str(q.statement.compile(compile_kwargs = {"literal_binds": True}))}')
        res = q.all()
        return [dict(zip(("version", "update_date"), x)) for x in res]


# Base class for DB Tables:
Base = declarative_base(cls=CommonTable)

# 初始化数据库连接:
engine = create_engine(get_config().SQLALCHEMY_DATABASE_URI)

# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
SessionLocal = sessionmaker(bind=engine)


# db Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_db_local():
    return SessionLocal()
