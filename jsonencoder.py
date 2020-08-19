import datetime
import decimal
import uuid
from werkzeug.http import http_date, text_type
from flask.json import JSONEncoder as _JSONEncoder
from flask import Flask as _Flask
from bson.objectid import ObjectId


class JSONEncoder(_JSONEncoder):
    """默认的Flask JSON编码器。这个版本扩展了默认的simplejson编码器，支持“datetime”对象、“UUID”对象和“Markup”对象，这些对象被序列化为RFC 822 datetime字符串(与HTTP日期格式相同)。为了支持更多的数据类型，请重写:meth: ' default '方法。
    """

    def default(self, o):
        """在子类中实现此方法，使其返回可序列化的对象'o'，或调用基本实现(引发'TypeError ')。
        例如，要支持任意迭代器，可以这样实现默认值::
            def default(self, o):
                try:
                    iterable = iter(o)
                except TypeError:
                    pass
                else:
                    return list(iterable)
                return JSONEncoder.default(self, o)
        """
        if isinstance(o, datetime.datetime):
            return o.strftime('%Y-%m-%d %H:%M:%S')
        if isinstance(o, datetime.date):
            return o.strftime('%Y-%m-%d')
        if isinstance(o, uuid.UUID):
            return str(o)
        if hasattr(o, '__html__'):
            return text_type(o.__html__())
        if isinstance(o, decimal.Decimal):
            return o.__float__()
        if isinstance(o, ObjectId):
            return str(o)
        return _JSONEncoder.default(self, o)


class Flask(_Flask):
    json_encoder = JSONEncoder
