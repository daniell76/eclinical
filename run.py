# -*- encoding: utf-8 -*-
"""
    Copyright(C) 2021 Calyx
    All rights reserved

    File : run.py
    Time : 2021/08/20 17:59:11
    Author : xiaf
    Version : 1.0
"""
import os.path

from app import create_app
import logging
from fastapi.logger import logger as fastapi_logger
from logging.handlers import RotatingFileHandler
import uvicorn


PROJ_DIR = os.path.dirname(__file__)
LOG_DIR = os.path.join(PROJ_DIR, "log")


def main():

    app = create_app()

    # save the log into the file
    formatter = logging.Formatter(
        "[%(asctime)s.%(msecs)03d] %(levelname)s [%(thread)d] - %(message)s", "%Y-%m-%d %H:%M:%S")
    handler = RotatingFileHandler(os.path.join(os.path.dirname(__file__), 'log', 'fastapi.log'), backupCount=0)
    logging.getLogger().setLevel(logging.NOTSET)
    fastapi_logger.addHandler(handler)
    handler.setFormatter(formatter)

    fastapi_logger.info('****************** Starting Server *****************')

    uvicorn.run(app, host="0.0.0.0", port=8000, workers=2)
    # uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == '__main__':
    main()
