# -*- coding: utf-8 -*-


# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------
import csv
import hashlib
import json
import os
import time

import redis

# -----------------------------------------------------------------------------
# Globals
# -----------------------------------------------------------------------------
import requests
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


def get_order_logistics_information(key=None, customer=None, phone="", order_from ="", to=""):
    key = key  # 客户授权key
    customer = customer  # 查询公司编号
    param = {
        'com': 'yunda',  # 查询的快递公司的编码，一律用小写字母
        'num': '3950055201640',  # 查询的快递单号，单号的最大长度是32个字符
        'phone': '',  # 收件人或寄件人的手机号或固话（也可以填写后四位，如果是固话，请不要上传分机号）
        'from': order_from,  # 出发地城市，省-市-区，非必填，填了有助于提升签收状态的判断的准确率，请尽量提供
        'to': '',  # 目的地城市，省-市-区，非必填，填了有助于提升签收状态的判断的准确率，且到达目的地后会加大监控频率，请尽量提供
        'resultv2': '1',  # 添加此字段表示开通行政区域解析功能。0：关闭（默认），1：开通行政区域解析功能，2：开通行政解析功能并且返回出发、目的及当前城市信息
        'show': '0',  # 返回数据格式。0：json（默认），1：xml，2：html，3：text
        'order': 'desc'  # 返回结果排序方式。desc：降序（默认），asc：升序
    }

    pjson = json.dumps(param)  # 转json字符串

    postdata = {
        'customer': customer,  # 查询公司编号
        'param': pjson  # 参数数据
    }

    # 签名加密， 用于验证身份， 按param + key + customer 的顺序进行MD5加密（注意加密后字符串要转大写）， 不需要“+”号
    str = pjson + key + customer
    md = hashlib.md5()
    md.update(str.encode())
    sign = md.hexdigest().upper()
    postdata['sign'] = sign  # 加密签名

    url = 'http://poll.kuaidi100.com/poll/query.do'  # 实时查询请求地址

    result = requests.post(url, postdata)  # 发送请求
    print(result.text)  # 返回数据

# -----------------------------------------------------------------------------
# Classes
# -----------------------------------------------------------------------------


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    order_logistics_information("yunda", "4307738980275")
