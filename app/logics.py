# -*- coding: utf-8 -*-


# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------
import csv
import os
import time

import redis

# -----------------------------------------------------------------------------
# Globals
# -----------------------------------------------------------------------------
import xlrd

REDIS = redis.StrictRedis(host='localhost', port=6379, decode_responses=True)
FILE_PATH = os.path.join(os.path.abspath(os.path.dirname(os.path.dirname(__file__))), "files")


# -----------------------------------------------------------------------------
# Functions
# -----------------------------------------------------------------------------

def refresh_expiration_time(token, data):
    REDIS.hmset(token, data)
    REDIS.expire(token, 7200)


def verify_token(token):
    query = REDIS.hgetall(token)
    if query:
        refresh_expiration_time(token, query)
        return True
    else:
        return False


def get_token_info(token):
    info = REDIS.hgetall(token)
    return info


def get_file_data(filename, strategy_id):
    xl = xlrd.open_workbook(os.path.join(FILE_PATH, filename))
    table = xl.sheets()[0]
    nrows = table.nrows  # 行数
    ncols = table.ncols  # 列数
    data = []
    for i in range(1, nrows):
        try:
            row = table.row_values(i)
            exchange_id = row[0].lower()
            instrument_id = row[1]
            instrument_type = row[2]
            tradingday = row[3]
            data.append(
                {
                    "strategy_id": strategy_id,
                    "exchange_id": exchange_id,
                    "instrument_id": instrument_id,
                    "instrument_type": int(instrument_type),
                    "tradingday": int(tradingday),
                }
            )
        except:
            pass
    return data

# -----------------------------------------------------------------------------
# Classes
# -----------------------------------------------------------------------------


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------
