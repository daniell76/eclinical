# -*- encoding: utf-8 -*-
"""
    Copyright(C) 2021 Calyx
    All rights reserved

    File : local.py
    Time : 2021/08/20 17:58:11
    Author : xiaf
    Version : 1.0
"""

import os
import uvicorn
from app import create_app


PROJ_DIR = os.path.dirname(__file__)
LOG_DIR = os.path.join(PROJ_DIR, "log")

LOG_CONFIG_FILE = os.path.join(PROJ_DIR, "logging.yaml")
# LOG_CONFIG = uvicorn.config.LOGGING_CONFIG


def main():

    app = create_app()

    uvicorn.run(app, host="0.0.0.0", port=8001, log_config=LOG_CONFIG_FILE)


if __name__ == "__main__":
    main()
