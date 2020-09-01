from jsonencoder import Flask
from flask import jsonify, request

static_address = "http://47.100.187.214:8081/"

# 初始化flask程序
app = Flask(__name__,
            static_folder="static",
            static_url_path="/static",
            template_folder="templates")
