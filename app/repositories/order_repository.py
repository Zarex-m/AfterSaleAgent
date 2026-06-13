from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.order import Order, OrderItem
from app.db.models.payment import Payment
from app.db.models.product import Product
from app.db.models.shipment import Shipment


async def list_orders(db: AsyncSession) -> list[Order]:
    result = await db.execute(select(Order).order_by(Order.created_at.desc()))
    return list(result.scalars().all())


async def get_order_by_no(db: AsyncSession, order_no: str) -> Order | None:
    result = await db.execute(select(Order).where(Order.order_no == order_no))
    return result.scalar_one_or_none()


async def get_order_items(db: AsyncSession, order_id: int) -> list[OrderItem]:
    result = await db.execute(select(OrderItem).where(OrderItem.order_id == order_id))
    return list(result.scalars().all())


async def get_payment_by_order_id(db: AsyncSession, order_id: int) -> Payment | None:
    result = await db.execute(select(Payment).where(Payment.order_id == order_id))
    return result.scalar_one_or_none()


async def get_shipment_by_order_id(db: AsyncSession, order_id: int) -> Shipment | None:
    result = await db.execute(select(Shipment).where(Shipment.order_id == order_id))
    return result.scalar_one_or_none()


async def get_products_by_ids(db: AsyncSession, product_ids: list[int]) -> list[Product]:
    if not product_ids:
        return []

    result = await db.execute(select(Product).where(Product.id.in_(product_ids)))
    return list(result.scalars().all())
