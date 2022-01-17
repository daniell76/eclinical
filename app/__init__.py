# -*- encoding: utf-8 -*-
"""
    Copyright(C) 2021 Calyx
    All rights reserved

    File : __init__.py
    Time : 2020/07/27 15:04:35
    Author : xiaf
    Version : 1.0
"""

import time
import logging
from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth_routers, user_routers, ctms_routers, rim_routers, admin_routers
from app.auth.auths import Auth
from fastapi.responses import JSONResponse


def create_app():
    """
    Create the Calyx dimensioning tool application, covering RIM and CTMS
    This web app calculates the cost estimation of each customer's deployment
    Database Structure:
        0. All tables has columns: id, update_username, create_username, create_date, update_date
        A. User inputs:
            rim_summary_records:
            ctms_summary_records:
            each user input summary entry is associated to a particular project and version.
            project is uniquely identified by uuid
            version is incremental for each project upon each modification
        B. project records:
            project_records: usually a project is for a particular customer's opportunity
                |-> env_summary_records: a project could have multiple of this entries.
                        There are actually 2 tiers: version -> env.
                        Version defines a particular estimation base on a set of input parameters
                        env defines the summary of a particular environment (prod/nonprod) of a given version
                    |-> detail_records:
                            details records define the bom of detailed components.
                            Each component belongs to a particular version and environment
        C. price elements:
            resource_prices: this table contains annual or oneoff price of each component
            currently exchange rate is hardcoded, only support USD/CNY
        D. Users:
            users: user login credential
    API input:
    API output:
    Operation:
        1. [optional] User load a project (and a particular version)
        2. User setup/modify parameters, and send request
        3. the app init/create a new version of a project, and calculate the estimation result
            a. parse the input parameter, and calculate the T-Shirt size
            b. load the T-shirt template and generate BoM list
            c. calculate estimated price based on BoM list
        4. [optional] User load the result of a project (and a particular version), modify the BoM list
        5. [optional] User re-calculate the result of a particular version based on adjusted BoM list
    """
    app = FastAPI()

    # create logger
    logger = logging.getLogger('fastapi')

    async def get_token_header(x_token: str = Header(...)):
        logger.info(f'x_token = "{x_token}"')
        if x_token != "fake-super-secret-token":
            raise HTTPException(status_code=400, detail="X-Token header invalid")

    origins = [
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8001",
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(
        auth_routers.router,
        prefix="/auth",
        tags=["auth"]
    )
    # app.include_router(
    #     items.router,
    #     prefix="/item",
    #     tags=["item"],
    #     dependencies=[Depends(get_token_header)],
    #     responses={404: {"description": "Not found"}},
    # )
    app.include_router(
        user_routers.router,
        prefix="/user",
        tags=["user"]
    )
    app.include_router(
        ctms_routers.router,
        prefix="/ctms",
        tags=["ctms"]
    )
    app.include_router(
        rim_routers.router,
        prefix="/rim",
        tags=["rim"]
    )
    app.include_router(
        admin_routers.router,
        prefix="/admin",
        tags=["admin"]
    )

    @app.middleware("http")
    async def process_authorization(request: Request, call_next):
        """
            在这个函数里统一对访问做权限token校验。
            1、如果是用户注册、登陆，那么不做token校验，由路径操作函数具体验证
            2、如果是其他操作，则需要从header或者cookie中取出token信息，解析出内容
               然后对用户身份进行验证，如果用户不存在则直接返回
               如果用户存在则将用户信息附加到request中，这样在后续的路径操作函数中可以直接使用。
        """
        start_time = time.time()

        # print(request.url)
        # print(request.url.path)
        print(request.method)

        if request.url.path in ['/auth/login', '/auth/register', '/auth/nope', '/docs', '/redoc', '/openapi.json']:
            logger.info('no jwt verify.')
        elif request.method in ['OPTIONS']:
            logger.info('no jwt verify.')
        else:
            logger.info('jwt verify.')

            result = Auth.identifyAll(request)
            if result['status'] and result['data']:
                user = result['data']['user']

                logger.info('jwt verify success. user: %s ' % user.username)

                # state中记录用户基本信息
                request.state.user = user
            else:
                return JSONResponse(content=result)

        # logger.info(request.url.path)

        response = await call_next(request)

        # logger.info(request.url.path)
        # logger.info(request.url.port)
        # logger.info(request.url.scheme)
        # logger.info(request.headers)
        # logger.info(request.cookies)

        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        return response

    return app
