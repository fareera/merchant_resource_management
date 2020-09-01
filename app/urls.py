from flask_restful import Api

#  加载API
from app.views import Auth, ApiDocs, BrandManager, ProductManager, PartnerProductManager, PartnerBrandManager, \
    UpdateProductStock, UpdateProductPrice, UpdateProductStatus, Logout, PartnerOrderManager, OrderManager, UploadImg, \
    GetStaticAddress, UserManagement

api = Api()
apiroot = '/api/v0.1/'
# # 接口文档
api.add_resource(ApiDocs,
                 "/",
                 endpoint='ApiDocs')
# 数据验证模块

# 登录模块
api.add_resource(Auth,
                 apiroot +
                 'auth',
                 endpoint='Auth')

# 品牌管理模块
api.add_resource(BrandManager,
                 apiroot +
                 'brand_manager',
                 endpoint='brand_manager')
# 商品管理模块
api.add_resource(ProductManager,
                 apiroot +
                 'product_manager',
                 endpoint='ProductManager')
api.add_resource(UpdateProductStock,
                 apiroot +
                 'UpdateProductStock',
                 endpoint='UpdateProductStock')

api.add_resource(UpdateProductPrice,
                 apiroot +
                 'UpdateProductPrice',
                 endpoint='UpdateProductPrice')

api.add_resource(UpdateProductStatus,
                 apiroot +
                 'UpdateProductStatus',
                 endpoint='UpdateProductStatus')
api.add_resource(UploadImg,
                 apiroot +
                 'UploadImg',
                 endpoint='UploadImg')

# 合作商商品管理模块
api.add_resource(PartnerProductManager,
                 apiroot +
                 'PartnerProductManager',
                 endpoint='PartnerProductManager')

# 登出
api.add_resource(Logout,
                 apiroot +
                 'Logout',
                 endpoint='Logout')
# 合作商品牌管理模块
api.add_resource(PartnerBrandManager,
                 apiroot +
                 'PartnerBrandManager',
                 endpoint='PartnerBrandManager')
# 合作商订单管理模块
api.add_resource(PartnerOrderManager,
                 apiroot +
                 'PartnerOrderManager',
                 endpoint='PartnerOrderManager')
# 订单管理模块
api.add_resource(OrderManager,
                 apiroot +
                 'OrderManager',
                 endpoint='OrderManager')
# 基本信息模块
api.add_resource(GetStaticAddress,
                 apiroot +
                 'GetStaticAddress',
                 endpoint='GetStaticAddress')

# 用户管理模块
api.add_resource(UserManagement,
                 apiroot +
                 'UserManagement',
                 endpoint='UserManagement')
