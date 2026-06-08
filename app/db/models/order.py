from datetime import datetime
from enum import StrEnum
from decimal import Decimal
from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey,Numeric

from app.db.base import Base

class OrderStatus(StrEnum):
    PENDING_PAYMENT="pending_payment"#待支付
    PAID="paid"#已支付未发货
    SHIPPED="shipped"#已发货
    DELIVERED="delivered"#已签收
    CANCELLED="cancelled"#已取消
    REFUNDED="refunded"#已退款
    PARTIALLY_REFUNDED="partially_refunded"#部分退款
    
class Order(Base):
    __tablename__="orders"
    
    id:Mapped[int]=mapped_column(primary_key=True)
    order_no:Mapped[str]=mapped_column(String(50),unique=True,index=True,nullable=False)
    customer_id:Mapped[int]=mapped_column(ForeignKey("customers.id"),nullable=False,index=True)
    status:Mapped[str]=mapped_column(String(50),default=OrderStatus.PENDING_PAYMENT.value,nullable=False)
    total_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    paid_at:Mapped[datetime]=mapped_column(DateTime,nullable=True)
    created_at:Mapped[datetime]=mapped_column(DateTime,default=datetime.utcnow,nullable=False)
    updated_at:Mapped[datetime]=mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )
    
class OrderItem(Base):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id"),
        index=True,
        nullable=False,
    )
    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id"),
        index=True,
        nullable=False,
    )
    quantity: Mapped[int] = mapped_column(nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )