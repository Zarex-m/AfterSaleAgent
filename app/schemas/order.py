from pydantic import BaseModel
from decimal import Decimal 
from datetime import datetime

# 订单列表项,一条记录代表一个订单
class OrderListItemResponse(BaseModel):
    id:int
    order_no:str
    customer_id:int
    status:str
    total_amount:Decimal
    paid_at:datetime|None
    created_at:datetime

    model_config = {"from_attributes": True}

#订单项详情
class OrderItemResponse(BaseModel):
    id:int
    product_id:int
    quantity:int
    unit_price:Decimal #下单时建议单价
    
    model_config = {"from_attributes": True}
    
#订单详情页
class OrderDetailResponse(OrderListItemResponse):
    id:int
    order_no:str
    customer_id:int
    status:str
    total_amount:Decimal
    paid_at:datetime|None
    created_at:datetime
    items:list[OrderItemResponse]
    
    model_config = {"from_attributes": True}

    
#订单支付信息
class PaymentResponse(BaseModel):
    id:int
    order_id:int
    amount:Decimal
    status:str
    paid_at:datetime|None
    refunded_amount:Decimal 
    
    model_config = {"from_attributes": True}

#订单物流信息
class ShipmentResponse(BaseModel):
    id:int
    order_id:int
    status:str
    carrier:str|None
    tracking_no:str|None
    shipped_at:datetime|None
    delivered_at:datetime|None
    
    model_config = {"from_attributes": True}