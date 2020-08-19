from jsonencoder import Flask
from flask import jsonify, request

# 初始化flask程序
app = Flask(__name__,
            static_folder="static",
            static_url_path="/static",
            template_folder="templates")
