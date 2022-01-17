# -*- coding: utf-8 -*-
"""
    Copyright (C) 2021 Calyx
    All rights reserved

    Filename : dateencoder.py
    Description : convert datetime type to json serializable.
                  ex:datetime.datetime is not JSON serializable

    Created by xiaf at 2021-08-20 17:50:00
"""

from datetime import datetime
import json


class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            print(obj.strftime('%Y-%m-%d %H:%M:%S.%f%Z'))
            return obj.strftime('%Y-%m-%d %H:%M:%S.%f%Z')
        else:
            return json.JSONEncoder.default(self, obj)



