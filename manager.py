from flasgger import Swagger
from flask import jsonify, abort, request, redirect
from werkzeug.exceptions import HTTPException, default_exceptions
from flask_cors import CORS

from app.errors import AuthError
from app.logics import verify_token
from settings import app
from app import create_app

create_app(app)
from app.urls import api

api.init_app(app)
CORS(app)
app.config['SWAGGER'] = {
    'title': 'My API',
    'uiversion': 3
}
swagger = Swagger(app)


def JsonApp(app):
    def error_handling(error):
        if isinstance(error, HTTPException):
            result = {"code": error.code,
                      "error": error.description, "msg": str(error)}
        else:
            description = abort.mapping[500].description
            result = {"code": 500, "error": description, "msg": str(error)}

        resp = jsonify(result)
        resp.status_code = result["code"]
        return resp

    for code in default_exceptions.keys():
        app.register_error_handler(code, error_handling)

    return app


# flask json序列化 全局返回404 500错误
# app = JsonApp(app)


# @app.before_request
# def do_something_whenever_a_request_comes_in():
#     # request is available
#
# @app.after_request
# def do_something_whenever_a_request_has_been_handled(response):
#     # we have a response to manipulate, always return one
#     return response
apiroot = '/api/v0.1/'
verify_paths = [
    "brand_manager",
    "ProductManager",
    "UpdateProductStock",
    "UpdateProductPrice",
    "UpdateProductStatus",
    "PartnerProductManager",
    "PartnerBrandManager",
    "Logout",
    "PartnerBrandManager",
    "PartnerOrderManager",
    "OrderManager",
    "GetStaticAddress",
    "UserManagement",
]



@app.before_request
def process():
    path = request.endpoint
    if path in verify_paths:
        token = request.args.get("token", None)
        if token is None:
            return jsonify({
                "error_id": AuthError.code,
                "error_msg": AuthError.__name__,
            })
        else:
            verify_res = verify_token(token)
            if not verify_res:
                return jsonify({
                    "error_id": AuthError.code,
                    "error_msg": AuthError.__name__,
                })


if __name__ == '__main__':
    app.run(port=8090)
