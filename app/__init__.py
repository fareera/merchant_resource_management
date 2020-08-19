import logging
from logging.handlers import RotatingFileHandler
from flask import request
import os

def create_app(app):
    """通过传入不同的配置名字，初始化其对应配置的应用实例"""

    # 配置项目日志
    # rbac = RBAC(app)  #引入权限控制
    # 配置
    # app.config['RBAC_USE_WHITE'] = True  #使用白名单

    app.before_request_funcs.setdefault(None, []).append(before_request)

def before_request():
    ip = request.remote_addr
    url = request.url
