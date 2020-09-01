from peewee import (
    Model,
    CharField,
    IntegerField,
    DateTimeField,
    DecimalField,
    PostgresqlDatabase,
    SqliteDatabase, AutoField, PrimaryKeyField
)

import datetime

# DBCONN = SqliteDatabase('webservice.db3', pragmas={'journal_mode': 'wal'})


DBCONN = PostgresqlDatabase('taoledb', **{
    'host': '106.54.253.253',
    'port': '5432',
    'user': 'taole',
    'password': 'taole2020!@'
})

class Brand(Model):
    id = PrimaryKeyField()
    name = CharField(max_length=50, null=False)
    create_time = DateTimeField(default=datetime.datetime.now)

    class Meta(object):
        """Indicates which database/schema this model points to."""

        database = DBCONN
        table_name = 'brand'


class Product(Model):
    sku_id = PrimaryKeyField()
    brand_id = IntegerField(null=False)
    name = CharField(max_length=200, null=False)
    unit = CharField(max_length=50, null=False)
    price = DecimalField(max_digits=20, decimal_places=3, null=False)
    stock = IntegerField(null=False)
    status = IntegerField(null=False)
    image = CharField(max_length=500, null=True)
    image_thumbnail = CharField(max_length=500, null=True)
    image_list = CharField(max_length=500, null=True)
    description = CharField(max_length=500)
    keywords = CharField(max_length=500)
    create_time = DateTimeField(default=datetime.datetime.now)
    update_time = DateTimeField(default=datetime.datetime.now)

    class Meta(object):
        """Indicates which database/schema this model points to."""

        database = DBCONN
        table_name = 'product'


class Order(Model):
    id = PrimaryKeyField()
    amount = DecimalField(max_digits=20, decimal_places=3, null=False)
    partner_id = IntegerField(null=False)
    status = IntegerField(null=False)
    create_time = DateTimeField(default=datetime.datetime.now)
    order_delivery_id = CharField(max_length=500 ,null=True)

    class Meta(object):
        """Indicates which database/schema this model points to."""
        database = DBCONN
        table_name = 'order'


class OrderDetail(Model):
    order_id = PrimaryKeyField()
    sku_id = IntegerField(null=False)
    volume = IntegerField(null=False)

    class Meta(object):
        """Indicates which database/schema this model points to."""

        database = DBCONN
        table_name = 'order_detail'


class Partner(Model):
    id = PrimaryKeyField()
    name = CharField(max_length=200, null=False)
    account = CharField(max_length=200, null=False)
    password = CharField(max_length=200, null=False)

    class Meta(object):
        """Indicates which database/schema this model points to."""

        database = DBCONN
        table_name = 'partner'


class PartnerHistory(Model):
    id = PrimaryKeyField()
    partner_id = IntegerField()
    operation = CharField(max_length=200, null=False)
    description = CharField(max_length=200, null=False)
    update_time = DateTimeField(default=datetime.datetime.now)

    class Meta(object):
        """Indicates which database/schema this model points to."""

        database = DBCONN
        table_name = 'partner_history'


class User(Model):
    id = PrimaryKeyField()
    name = CharField(max_length=200, null=False)
    account = CharField(max_length=200, null=False)
    password = CharField(max_length=200, null=False)

    class Meta(object):
        database = DBCONN
        table_name = 'user'




# DBCONN.create_tables([User,Product,Partner,PartnerHistory,Order,OrderDetail,Brand])


