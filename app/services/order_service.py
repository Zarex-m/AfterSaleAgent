from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.order import Order, OrderItem
from app.db.models.payment import Payment
from app.db.models.shipment import Shipment
from app.repositories import order_repository


def _decimal_to_float(value):
    return float(value) if value is not None else None


def _datetime_to_iso(value):
    return value.isoformat() if value is not None else None

#列出订单列表   
async def list_orders(db: AsyncSession) -> list[Order]:
    return await order_repository.list_orders(db)

async def get_order_by_no(db: AsyncSession, order_no: str) -> Order | None:
    return await order_repository.get_order_by_no(db, order_no)

async def get_order_items(db: AsyncSession, order_id: int) -> list[OrderItem]:
    return await order_repository.get_order_items(db, order_id)

async def get_payment_by_order_id(db: AsyncSession, order_id: int) -> Payment | None:
    return await order_repository.get_payment_by_order_id(db, order_id)

async def get_shipment_by_order_id(db: AsyncSession, order_id: int) -> Shipment | None:
    return await order_repository.get_shipment_by_order_id(db, order_id)


async def get_order_context_by_no(
    db: AsyncSession,
    order_no: str,
) -> dict | None:
    order = await order_repository.get_order_by_no(db, order_no)
    if order is None:
        return None

    items = await order_repository.get_order_items(db, order.id)
    payment = await order_repository.get_payment_by_order_id(db, order.id)
    shipment = await order_repository.get_shipment_by_order_id(db, order.id)

    product_ids = [item.product_id for item in items]
    products = await order_repository.get_products_by_ids(db, product_ids)
    product_by_id = {product.id: product for product in products}

    return {
        "order": {
            "id": order.id,
            "order_no": order.order_no,
            "customer_id": order.customer_id,
            "status": order.status,
            "total_amount": _decimal_to_float(order.total_amount),
            "paid_at": _datetime_to_iso(order.paid_at),
            "created_at": _datetime_to_iso(order.created_at),
        },
        "items": [
            {
                "id": item.id,
                "product_id": item.product_id,
                "quantity": item.quantity,
                "unit_price": _decimal_to_float(item.unit_price),
                "product": (
                    {
                        "id": product_by_id[item.product_id].id,
                        "name": product_by_id[item.product_id].name,
                        "category": product_by_id[item.product_id].category,
                        "is_virtual": product_by_id[item.product_id].is_virtual,
                        "is_fresh": product_by_id[item.product_id].is_fresh,
                        "price": _decimal_to_float(product_by_id[item.product_id].price),
                    }
                    if item.product_id in product_by_id
                    else None
                ),
            }
            for item in items
        ],
        "payment": (
            {
                "id": payment.id,
                "status": payment.status,
                "amount": _decimal_to_float(payment.amount),
                "refunded_amount": _decimal_to_float(payment.refunded_amount),
                "paid_at": _datetime_to_iso(payment.paid_at),
            }
            if payment
            else None
        ),
        "shipment": (
            {
                "id": shipment.id,
                "status": shipment.status,
                "carrier": shipment.carrier,
                "tracking_no": shipment.tracking_no,
                "shipped_at": _datetime_to_iso(shipment.shipped_at),
                "delivered_at": _datetime_to_iso(shipment.delivered_at),
            }
            if shipment
            else None
        ),
        "products": [
            {
                "id": product.id,
                "name": product.name,
                "category": product.category,
                "is_virtual": product.is_virtual,
                "is_fresh": product.is_fresh,
                "price": _decimal_to_float(product.price),
            }
            for product in products
        ],
    }
