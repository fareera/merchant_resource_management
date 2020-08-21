from jsonencoder import Flask
from flask import jsonify, request

static_address = "http://122.51.70.209:8081/"

# 初始化flask程序
app = Flask(__name__,
            static_folder="static",
            static_url_path="/static",
            template_folder="templates")
