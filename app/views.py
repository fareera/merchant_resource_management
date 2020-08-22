# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------
import datetime
import json
import xlwt
import logging
import os
import time
import uuid
from decimal import Decimal

from flask import request, jsonify, redirect
from flask_restful import Resource
from werkzeug.utils import secure_filename
from app.models.orm import Brand, User, Partner, Order, Product, DBCONN, OrderDetail

from app.errors import IntervalServerError, AuthError, InvalidParameter
from app.logics import refresh_expiration_time, verify_token, REDIS, get_token_info, get_file_data

# -----------------------------------------------------------------------------
# Globals
# -----------------------------------------------------------------------------
from settings import static_address

FILE_PATH = os.path.join(os.path.abspath(os.path.dirname(os.path.dirname(__file__))), "files")


# ----------------------------------------------------------------------------
# Functions
# -----------------------------------------------------------------------------
def get_pagesize(perpage, count):
    """获取页数"""
    if count:
        if count > perpage:
            if count % perpage == 0:
                return count // perpage
            else:
                return (count // perpage) + 1
        else:
            return 1
    else:
        return 0


# -----------------------------------------------------------------------------
# Classes
# -----------------------------------------------------------------------------
class ApiDocs(Resource):
    def get(self):
        return redirect('/apidocs')


class BackendApi(Resource):
    @staticmethod
    def make_response(error_id=200, error_msg="success", **kwargs):
        response = kwargs
        response.update(error_id=error_id, error_msg=error_msg)
        return jsonify(response)


class Auth(BackendApi):
    def post(self):
        """
        登录模块
        ---
        tags:
          - 鉴权模块
        parameters:
          - name: account
            in: body
            type: string
            required: true
            description: 账号
          - name: password
            in: body
            type: string
            description: 密码
          - name: role
            in: body
            type: string
            description: 用户类型 (user|partner)
        responses:
          500:
            description: Server Error !
        """
        try:
            json_parameter = request.get_json(force=True)
            account = json_parameter["account"]
            password = json_parameter["password"]
            role = json_parameter["role"]
            query_res = None
            token = str(uuid.uuid4())
            data = dict()
            if role == "user":
                query_res = User.select(User.id).where(
                    (User.account == account) &
                    (User.password == password)
                )
                data["user_type"] = "user"
            elif role == "partner":
                query_res = Partner.select(Partner.id).where(
                    (Partner.account == account) &
                    (Partner.password == password)
                )
                data["user_type"] = "partner"
            data["user_id"] = query_res[0].id
            if query_res:
                refresh_expiration_time(token, data)
                return self.make_response(token=token)
            else:
                return self.make_response(error_id=AuthError.code, error_msg=AuthError.__name__)
        except Exception as e:
            logging.error(e)
            return self.make_response(error_id=IntervalServerError.code, error_msg=str(e))


class BrandManager(BackendApi):
    def get(self):
        """
        获取所有品牌
        ---
        tags:
          - 品牌管理
        responses:
          500:
            description: Server Error !
        """
        try:
            query_res = Brand.select().dicts()
            result = [query_obj for query_obj in query_res]
            return self.make_response(reult=result)
        except Exception as e:
            logging.error(e)
            return self.make_response(error_id=IntervalServerError.code, error_msg=str(e))

    def post(self):
        """
        创建品牌
        ---
        tags:
          - 品牌管理
        parameters:
          - name: name
            in: query
            type: string
            required: true
            description: 品牌名
        responses:
          500:
            description: Server Error !
        """
        try:
            name = request.args.get("name")
            Brand.insert(
                {
                    "name": name,
                    "create_time": datetime.datetime.now()
                }
            ).execute()
            return self.make_response()
        except Exception as e:
            logging.error(e)
            return self.make_response(error_id=IntervalServerError.code, error_msg=str(e))

    def delete(self):
        """
        删除品牌
        ---
        tags:
          - 品牌管理
        parameters:
          - name: id
            in: query
            type: int
            required: true
            description: 品牌id
        responses:
          500:
            description: Server Error !
        """
        try:
            id = request.args.get("id")
            query_res = Brand.select().where(Brand.id == id)
            for i in query_res:
                i.delete_instance()
            return self.make_response()
        except Exception as e:
            logging.error(e)
            return self.make_response(error_id=IntervalServerError.code, error_msg=str(e))


class ProductManager(BackendApi):
    def get(self):
        """
        获取所有商品
        ---
        tags:
          - 商品管理
        responses:
          500:
            description: Server Error !
        """
        try:
            query_res = Product.select().dicts()
            result = [query_obj for query_obj in query_res]
            return self.make_response(reult=result)
        except Exception as e:
            logging.error(e)
            return self.make_response(error_id=IntervalServerError.code, error_msg=str(e))

    def post(self):
        """
        创建商品
        ---
        tags:
          - 商品管理
        parameters:
          - name: brand_id
            in: body
            type: int
            required: true
            description: 商品品牌id，品牌表外键
          - name: name
            in: body
            type: string
            required: true
            description: 商品名称
          - name: unit
            in: body
            type: string
            required: true
            description: 商品计件单位
          - name: price
            in: body
            type: decimal
            required: true
            default: 1.77
            description: 商品单价,类型小数
          - name: stock
            in: body
            type: int
            required: true
            description: 商品库存
          - name: status
            in: body
            type: int
            required: true
            description: 商品状态 0-下架 1-上架
          - name: image
            in: body
            type: string
            required: true
            description: 商品主图名
          - name: image_thumbnail
            in: body
            type: string
            required: true
            description: 商品缩略图名
          - name: image_list
            in: body
            type: string
            required: true
            description: 商品详情图文件名，逗号分隔
          - name: description
            in: body
            type: string
            required: true
            description: 商品详情介绍（后台网页提供html格式的文本编辑器，存escape后的文字）
          - name: keywords
            in: body
            type: string
            required: true
            description: 关键词，逗号分隔
        responses:
          500:
            description: Server Error !
        """
        try:
            json_parameter = request.get_json(force=True)
            json_parameter["create_time"] = datetime.datetime.now()
            json_parameter["update_time"] = datetime.datetime.now()
            json_parameter["price"] = Decimal(json_parameter["price"])
            Product.insert(json_parameter).execute()
            return self.make_response()
        except Exception as e:
            logging.error(e)
            return self.make_response(error_id=IntervalServerError.code, error_msg=str(e))

    def delete(self):
        """
        删除商品
        ---
        tags:
          - 商品管理
        parameters:
          - name: sku_id
            in: query
            type: int
            required: true
            description: 商品id
        responses:
          500:
            description: Server Error !
        """
        try:
            sku_id = request.args.get("sku_id")
            query_res = Product.select().where(Product.sku_id == sku_id)
            for i in query_res:
                i.delete_instance()
            return self.make_response()
        except Exception as e:
            logging.error(e)
            return self.make_response(error_id=IntervalServerError.code, error_msg=str(e))

    def put(self):
        """
        修改商品基本资料
        ---
        tags:
          - 商品管理
        parameters:
          - name: brand_id
            in: body
            type: int
            required: true
            description: 商品品牌id，品牌表外键
          - name: sku_id
            in: body
            type: int
            required: true
            description: 商品id
          - name: name
            in: body
            type: string
            required: true
            description: 商品名称
          - name: unit
            in: body
            type: string
            required: true
            description: 商品计件单位
          - name: price
            in: body
            type: decimal
            required: true
            default: 1.77
            description: 商品单价,类型小数
          - name: stock
            in: body
            type: int
            required: true
            description: 商品库存
          - name: status
            in: body
            type: int
            required: true
            description: 商品状态 0-下架 1-上架
          - name: image
            in: body
            type: string
            required: true
            description: 商品主图名称
          - name: image_thumbnail
            in: body
            type: string
            required: true
            description: 商品缩略图名称
          - name: image_list
            in: body
            type: string
            required: true
            description: 商品详情图名称，逗号分隔
          - name: description
            in: body
            type: string
            required: true
            description: 商品详情介绍（后台网页提供html格式的文本编辑器，存escape后的文字）
          - name: keywords
            in: body
            type: string
            required: true
            description: 关键词，逗号分隔
        responses:
          500:
            description: Server Error !
        """
        try:
            json_parameter = request.get_json(force=True)
            json_parameter["update_time"] = datetime.datetime.now()
            json_parameter["price"] = Decimal(json_parameter["price"])
            sku_id = json_parameter["sku_id"]
            del json_parameter["sku_id"]
            Product.update(json_parameter).where(Product.sku_id == sku_id).execute()
            return self.make_response()
        except Exception as e:
            logging.error(e)
            return self.make_response(error_id=IntervalServerError.code, error_msg=str(e))


class UploadImg(BackendApi):
    def post(self):
        """
        上传图片
        ---
        tags:
          - 商品管理
        parameters:
          - name: token
            in: query
            type: string
            required: ture
            description: token
          - name: img
            in: body
            type: img
            required: ture
            description: 图片文件
        responses:
          500:
            description: Server Error !
        """
        img = request.files.get('img')
        filename = str(img.filename).strip('"').split(".")
        filename = filename[0] + "_" + str(uuid.uuid4()) + "." + filename[1]
        file_path = os.path.join(FILE_PATH, filename)
        img.save(file_path)
        return self.make_response(filename=filename)


class PartnerBrandManager(BackendApi):
    def get(self):
        """
        合作商获取所有品牌
        ---
        tags:
          - 合作商品牌管理
        parameters:
          - name: token
            in: query
            type: string
            required: ture
            description: token
        responses:
          500:
            description: Server Error !
        """
        try:
            query_res = Brand.select(Brand.name, Brand.create_time).dicts()
            result = [query_obj for query_obj in query_res]
            return self.make_response(reult=result)
        except Exception as e:
            logging.error(e)
            return self.make_response(error_id=IntervalServerError.code, error_msg=str(e))


class PartnerProductManager(BackendApi):
    def get(self):
        """
        合作商获取所有商品
        ---
        tags:
          - 合作商商品管理
        parameters:
          - name: brand_name
            in: query
            type: string
            required: false
            description: 品牌名称
          - name: page_size
            in: query
            type: int
            required: false
            default: 10
            description: 每页展示数量
          - name: page
            in: query
            type: int
            required: ture
            default: 1
            description: 页数
          - name: token
            in: query
            type: string
            required: ture
            description: token
        responses:
          500:
            description: Server Error !
        """
        try:
            brand_name = request.args.get("brand_name", None)
            page = request.args.get("page", 1)
            page_size = request.args.get("page_size", 10)
            brand_id = None
            if brand_name:
                query_res = Brand.select().where(Brand.name == brand_name)
                if query_res:
                    brand_id = query_res[0].id
            all_count = Product.select(
                Product.sku_id,
            ).where(
                Product.brand_id == brand_id if brand_id is not None else 1 == 1
            ).count()
            total_page = get_pagesize(page_size, all_count)
            query_res = Product.select().where(
                Product.brand_id == brand_id if brand_id is not None else 1 == 1
            ).ordey_by(Product.create_time.desc()).paginate(int(page), page_size).dicts()
            query_res = list(query_res)
            return self.make_response(reult=query_res, total_page=total_page)
        except Exception as e:
            logging.error(e)
            return self.make_response(error_id=IntervalServerError.code, error_msg=str(e))


class PartnerOrderManager(BackendApi):
    def post(self):
        """
        下单
        ---
        tags:
          - 合作商订单管理
        parameters:
          - name: skus
            in: body
            type: array
            required: ture
            description: 下单商品列表
            example: [ {"sku_id" : 1 , "volume" : 3}]
          - name: token
            in: query
            type: string
            required: ture
            description: token
        responses:
          500:
            description: Server Error !
        """
        # try:
        token = request.args.get("token", None)
        json_parameter = request.get_json(force=True)
        skus = json_parameter["skus"]
        print(skus)
        print(type(skus))
        data = REDIS.hgetall(token)
        parter_id = int(data["user_id"])
        amount = 0
        for sku in skus:
            sku_id = sku["sku_id"]
            volume = sku["volume"]
            amount += (list(Product.select(Product.price).where(
                Product.sku_id == int(sku_id)).dicts())[0]["price"] * int(
                volume))

        with DBCONN.atomic():
            order_id = Order.insert(
                {
                    "amount": Decimal(amount),
                    "partner_id": parter_id,
                    "status": 0,
                    "create_time": datetime.datetime.now(),
                }
            ).execute()
            for sku in skus:
                OrderDetail.insert(
                    {
                        "order_id": int(order_id),
                        "sku_id": int(sku["sku_id"]),
                        "volume": int(sku["volume"]),
                    }
                ).execute()
        return self.make_response()
        # except Exception as e:
        #     logging.error(e)
        #     return self.make_response(error_id=IntervalServerError.code, error_msg=str(e))


class OrderManager(BackendApi):
    def post(self):
        """
        订单导出xlsx
        ---
        tags:
          - 订单管理
        parameters:
          - name: partner_id
            in: query
            type: int
            required: false
            description: 合作商id
          - name: token
            in: query
            type: string
            required: ture
            description: token
          - name: start_time
            in: query
            type: string
            required: false
            default: ""
            description: 起始时间
          - name: end_time
            in: query
            type: string
            required: false
            default: ""
            description: 结束时间
        responses:
          500:
            description: Server Error !
        """
        try:
            workbook = xlwt.Workbook(encoding='utf-8')
            booksheet = workbook.add_sheet('Sheet 1', cell_overwrite_ok=True)
            partner_id = request.args.get("partner_id", None)
            start_time = request.args.get("start_time", None)
            end_time = request.args.get("end_time", None)
            if start_time:
                start_time = datetime.datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
            if end_time:
                end_time = datetime.datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")
            query_res = Order.select().where(
                (Order.id == int(partner_id) if partner_id is not None else 1 == 1) &
                (Order.create_time >= start_time if start_time else 1 == 1) &
                (Order.create_time <= end_time if end_time else 1 == 1)
            ).order_by(Order.create_time.desc()).dicts()
            query_res = list(query_res)
            for q in query_res:
                orderdetail_query = OrderDetail.select().where(OrderDetail.order_id == q["id"]).dicts()
                sku_msg = []
                for oq in orderdetail_query:
                    sku_query = list(Product.select().where(Product.sku_id == oq["sku_id"]).dicts())[0]
                    oq["sku_detail"] = sku_query
                    sku_msg.append(oq)
                q["sku_msg"] = sku_msg
                partner_query = Partner.select(Partner.name).where(Partner.id == q["partner_id"]).dicts()
                q["partner_msg"] = list(partner_query)[0]
            result = [query_obj for query_obj in query_res]
            export_data = []
            export_data.append(
                ["创建时间", "订单id", "合作商id", "合作商名称", "物流订单号", "商品名称", "下单数量", "单价", "订单价格"]
            )
            for i in result:
                for skm in i["sku_msg"]:
                    export_data.append(
                        [i["create_time"], i["id"], i["create_time"], i["partner_msg"]["name"], i["order_delivery_id"],
                         skm["sku_detail"]["name"], skm["volume"],
                         skm["sku_detail"]["price"], i["amount"]]
                    )
            for i, row in enumerate(export_data):
                for j, col in enumerate(row):
                    booksheet.write(i, j, col)
            filename = "{}.xlsx".format(str(uuid.uuid4()))
            workbook.save(os.path.join(FILE_PATH, filename))
            return self.make_response(filename=filename)
        except Exception as e:
            logging.error(e)
            return self.make_response(error_id=IntervalServerError.code, error_msg=str(e))

    def put(self):
        """
        修改物流编号
        ---
        tags:
          - 订单管理
        parameters:
          - name: order_id
            in: body
            type: int
            required: ture
            description: 订单id
          - name: order_delivery_id
            in: body
            type: string
            required: ture
            description: 订单物流编号
          - name: token
            in: query
            type: string
            required: ture
            description: token
        responses:
          500:
            description: Server Error !
        """
        json_parameter = request.get_json(force=True)
        order_id = json_parameter["order_id"]
        del json_parameter["order_id"]
        Order.update(
            json_parameter
        ).where(Order.id == order_id).execute()
        return self.make_response()

    def get(self):
        """
        查看订单
        ---
        tags:
          - 订单管理
        parameters:
          - name: partner_id
            in: query
            type: int
            required: false
            description: 合作商id
          - name: page_size
            in: query
            type: int
            required: false
            default: 10
            description: 每页展示数量
          - name: start_time
            in: query
            type: string
            required: false
            default: ""
            description: 起始时间
          - name: end_time
            in: query
            type: string
            required: false
            default: ""
            description: 结束时间
          - name: page
            in: query
            type: int
            required: ture
            default: 1
            description: 页数
          - name: token
            in: query
            type: string
            required: ture
            description: token
        responses:
          500:
            description: Server Error !
        """
        try:
            page = request.args.get("page", 1)
            partner_id = request.args.get("partner_id", None)
            start_time = request.args.get("start_time", None)
            end_time = request.args.get("end_time", None)
            if start_time:
                start_time = datetime.datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
            if end_time:
                end_time = datetime.datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")
            page_size = request.args.get("page_size", 10)
            all_count = Order.select(
                Order.id
            ).count()
            total_page = get_pagesize(page_size, all_count)
            query_res = Order.select().where(
                (Order.id == int(partner_id) if partner_id is not None else 1 == 1) &
                (Order.create_time >= start_time if start_time else 1 == 1) &
                (Order.create_time <= end_time if end_time else 1 == 1)
            ).order_by(Order.create_time.desc()).paginate(int(page), page_size).dicts()
            query_res = list(query_res)
            for q in query_res:
                orderdetail_query = OrderDetail.select().where(OrderDetail.order_id == q["id"]).dicts()
                sku_msg = []
                for oq in orderdetail_query:
                    sku_query = list(Product.select().where(Product.sku_id == oq["sku_id"]).dicts())[0]
                    oq["sku_detail"] = sku_query
                    sku_msg.append(oq)
                q["sku_msg"] = sku_msg
                partner_query = Partner.select(Partner.name).where(Partner.id == q["partner_id"]).dicts()
                q["partner_msg"] = list(partner_query)[0]
            result = [query_obj for query_obj in query_res]
            return self.make_response(reult=result, total_page=total_page)
        except Exception as e:
            logging.error(e)
            return self.make_response(error_id=IntervalServerError.code, error_msg=str(e))


class UpdateProductPrice(BackendApi):
    def put(self):
        """
        修改商品价格
        ---
        tags:
          - 商品管理
        parameters:
          - name: token
            in: query
            type: string
            required: ture
            description: token
          - name: brand_id
            in: body
            type: int
            required: true
            description: 商品品牌id，品牌表外键
          - name: sku_id
            in: body
            type: int
            required: true
            description: 商品id
          - name: name
            in: body
            type: string
            required: true
            description: 商品名称
          - name: unit
            in: body
            type: string
            required: true
            description: 商品计件单位
          - name: price
            in: body
            type: decimal
            required: true
            default: 1.77
            description: 商品单价,类型小数
          - name: stock
            in: body
            type: int
            required: true
            description: 商品库存
          - name: status
            in: body
            type: int
            required: true
            description: 商品状态 0-下架 1-上架
          - name: image
            in: body
            type: string
            required: true
            description: 商品主图http链接（nginx服务器代理）
          - name: image_thumbnail
            in: body
            type: string
            required: true
            description: 商品缩略图http链接
          - name: image_list
            in: body
            type: string
            required: true
            description: 商品详情图http链接，逗号分隔
          - name: description
            in: body
            type: string
            required: true
            description: 商品详情介绍（后台网页提供html格式的文本编辑器，存escape后的文字）
          - name: keywords
            in: body
            type: string
            required: true
            description: 关键词，逗号分隔
        responses:
          500:
            description: Server Error !
        """
        try:
            json_parameter = request.get_json(force=True)
            json_parameter["update_time"] = datetime.datetime.now()
            json_parameter["price"] = Decimal(json_parameter["price"])
            sku_id = json_parameter["sku_id"]
            del json_parameter["sku_id"]
            Product.update(json_parameter).where(Product.sku_id == sku_id).execute()
            return self.make_response()
        except Exception as e:
            logging.error(e)
            return self.make_response(error_id=IntervalServerError.code, error_msg=str(e))


class UpdateProductStock(BackendApi):
    def put(self):
        """
        修改商品库存
        ---
        tags:
          - 商品管理
        parameters:
          - name: brand_id
            in: body
            type: int
            required: true
            description: 商品品牌id，品牌表外键
          - name: sku_id
            in: body
            type: int
            required: true
            description: 商品id
          - name: name
            in: body
            type: string
            required: true
            description: 商品名称
          - name: unit
            in: body
            type: string
            required: true
            description: 商品计件单位
          - name: price
            in: body
            type: decimal
            required: true
            default: 1.77
            description: 商品单价,类型小数
          - name: stock
            in: body
            type: int
            required: true
            description: 商品库存
          - name: status
            in: body
            type: int
            required: true
            description: 商品状态 0-下架 1-上架
          - name: image
            in: body
            type: string
            required: true
            description: 商品主图http链接（nginx服务器代理）
          - name: image_thumbnail
            in: body
            type: string
            required: true
            description: 商品缩略图http链接
          - name: image_list
            in: body
            type: string
            required: true
            description: 商品详情图http链接，逗号分隔
          - name: description
            in: body
            type: string
            required: true
            description: 商品详情介绍（后台网页提供html格式的文本编辑器，存escape后的文字）
          - name: keywords
            in: body
            type: string
            required: true
            description: 关键词，逗号分隔
        responses:
          500:
            description: Server Error !
        """
        try:
            json_parameter = request.get_json(force=True)
            json_parameter["update_time"] = datetime.datetime.now()
            json_parameter["price"] = Decimal(json_parameter["price"])
            sku_id = json_parameter["sku_id"]
            del json_parameter["sku_id"]
            Product.update(json_parameter).where(Product.sku_id == sku_id).execute()
            return self.make_response()
        except Exception as e:
            logging.error(e)
            return self.make_response(error_id=IntervalServerError.code, error_msg=str(e))


class UpdateProductStatus(BackendApi):
    def put(self):
        """
        商品上下架
        ---
        tags:
          - 商品管理
        parameters:
          - name: brand_id
            in: body
            type: int
            required: true
            description: 商品品牌id，品牌表外键
          - name: sku_id
            in: body
            type: int
            required: true
            description: 商品id
          - name: name
            in: body
            type: string
            required: true
            description: 商品名称
          - name: unit
            in: body
            type: string
            required: true
            description: 商品计件单位
          - name: price
            in: body
            type: decimal
            required: true
            default: 1.77
            description: 商品单价,类型小数
          - name: stock
            in: body
            type: int
            required: true
            description: 商品库存
          - name: status
            in: body
            type: int
            required: true
            description: 商品状态 0-下架 1-上架
          - name: image
            in: body
            type: string
            required: true
            description: 商品主图http链接（nginx服务器代理）
          - name: image_thumbnail
            in: body
            type: string
            required: true
            description: 商品缩略图http链接
          - name: image_list
            in: body
            type: string
            required: true
            description: 商品详情图http链接，逗号分隔
          - name: description
            in: body
            type: string
            required: true
            description: 商品详情介绍（后台网页提供html格式的文本编辑器，存escape后的文字）
          - name: keywords
            in: body
            type: string
            required: true
            description: 关键词，逗号分隔
        responses:
          500:
            description: Server Error !
        """
        try:
            json_parameter = request.get_json(force=True)
            json_parameter["update_time"] = datetime.datetime.now()
            json_parameter["price"] = Decimal(json_parameter["price"])
            sku_id = json_parameter["sku_id"]
            del json_parameter["sku_id"]
            Product.update(json_parameter).where(Product.sku_id == sku_id).execute()
            return self.make_response()
        except Exception as e:
            logging.error(e)
            return self.make_response(error_id=IntervalServerError.code, error_msg=str(e))


class Logout(BackendApi):
    def delete(self):
        """
        登出
        ---
        tags:
          - 鉴权模块
        parameters:
          - name: token
            in: query
            type: string
            required: ture
            description: token
        responses:
          500:
            description: Server Error !
        """
        token = request.args.get("token")
        REDIS.delete(token)
        return self.make_response()


class GetStaticAddress(BackendApi):
    def get(self):
        """
        获取服务器静态文件访问地址
        ---
        tags:
          - 基本信息模块
        parameters:
          - name: token
            in: query
            type: string
            required: ture
            description: token
        responses:
          500:
            description: Server Error !
        """
        return self.make_response(address=static_address)


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    pass
