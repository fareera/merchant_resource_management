from app.models.orm import User, Product, Partner, PartnerHistory, Order, OrderDetail, Brand

from app.models.orm_sqlite import User as user, Product as product, Partner as partner, \
    PartnerHistory as partnerhistory, Order as order, OrderDetail as orderdetail, Brand as brand

res = user.select().dicts()
for i in res:
    User.insert(
        i
    ).execute()
res = product.select().dicts()
for i in res:
    i["image"] = i["image"].replace("http://122.51.70.209:8081/","")
    i["image_thumbnail"] = i["image_thumbnail"].replace("http://122.51.70.209:8081/","")
    i["image_list"] = i["image_list"].replace("http://122.51.70.209:8081/","")
    Product.insert(
        i
    ).execute()
res = partner.select().dicts()
for i in res:
    Partner.insert(
        i
    ).execute()
res = partnerhistory.select().dicts()
for i in res:
    PartnerHistory.insert(
        i
    ).execute()
res = order.select().dicts()
for i in res:
    Order.insert(
        i
    ).execute()
res = orderdetail.select().dicts()
for i in res:
    OrderDetail.insert(
        i
    ).execute()
res = brand.select().dicts()
for i in res:
    Brand.insert(
        i
    ).execute()
