import asyncio
import sys
from datetime import datetime, timedelta
from decimal import Decimal
from pathlib import Path

from sqlalchemy import select

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.db.models.customer import Customer, CustomerLevel
from app.db.models.order import Order, OrderItem, OrderStatus
from app.db.models.payment import Payment, PaymentStatus
from app.db.models.product import Product, ProductCategory
from app.db.models.shipment import Shipment, ShipmentStatus
from app.db.session import SessionLocal


DEMO_ORDER_NOS = ["10086", "10087", "10088"]


async def seed_demo_data() -> None:
    async with SessionLocal() as db:
        existing_result = await db.execute(
            select(Order.id).where(Order.order_no.in_(DEMO_ORDER_NOS)).limit(1)
        )
        if existing_result.scalar_one_or_none() is not None:
            print("Demo data already exists, skip.")
            return

        now = datetime.utcnow().replace(microsecond=0)
        delivered_at = now - timedelta(days=2)
        paid_at = now - timedelta(days=3)

        customer_normal = Customer(
            name="Zhang San",
            phone="13800000001",
            level=CustomerLevel.NORMAL.value,
        )
        customer_vip = Customer(
            name="Li Si",
            phone="13800000002",
            level=CustomerLevel.VIP.value,
        )
        customer_normal_2 = Customer(
            name="Wang Wu",
            phone="13800000003",
            level=CustomerLevel.NORMAL.value,
        )

        product_normal = Product(
            name="Cotton T-Shirt",
            category=ProductCategory.CLOTHING.value,
            is_virtual=False,
            is_fresh=False,
            price=Decimal("99.00"),
        )
        product_high_value = Product(
            name="Noise Cancelling Headphones Pro",
            category=ProductCategory.ELECTRONICS.value,
            is_virtual=False,
            is_fresh=False,
            price=Decimal("1299.00"),
        )
        product_virtual = Product(
            name="Annual Membership Redeem Code",
            category=ProductCategory.VIRTUAL_GOODS.value,
            is_virtual=True,
            is_fresh=False,
            price=Decimal("199.00"),
        )

        db.add_all(
            [
                customer_normal,
                customer_vip,
                customer_normal_2,
                product_normal,
                product_high_value,
                product_virtual,
            ]
        )
        await db.flush()

        order_10086 = Order(
            order_no="10086",
            customer_id=customer_normal.id,
            status=OrderStatus.DELIVERED.value,
            total_amount=Decimal("99.00"),
            paid_at=paid_at,
        )
        order_10087 = Order(
            order_no="10087",
            customer_id=customer_vip.id,
            status=OrderStatus.DELIVERED.value,
            total_amount=Decimal("1299.00"),
            paid_at=paid_at,
        )
        order_10088 = Order(
            order_no="10088",
            customer_id=customer_normal_2.id,
            status=OrderStatus.DELIVERED.value,
            total_amount=Decimal("199.00"),
            paid_at=paid_at,
        )

        db.add_all([order_10086, order_10087, order_10088])
        await db.flush()

        db.add_all(
            [
                OrderItem(
                    order_id=order_10086.id,
                    product_id=product_normal.id,
                    quantity=1,
                    unit_price=Decimal("99.00"),
                ),
                OrderItem(
                    order_id=order_10087.id,
                    product_id=product_high_value.id,
                    quantity=1,
                    unit_price=Decimal("1299.00"),
                ),
                OrderItem(
                    order_id=order_10088.id,
                    product_id=product_virtual.id,
                    quantity=1,
                    unit_price=Decimal("199.00"),
                ),
                Payment(
                    order_id=order_10086.id,
                    amount=Decimal("99.00"),
                    status=PaymentStatus.PAID.value,
                    paid_at=paid_at,
                    refunded_amount=Decimal("0.00"),
                ),
                Payment(
                    order_id=order_10087.id,
                    amount=Decimal("1299.00"),
                    status=PaymentStatus.PAID.value,
                    paid_at=paid_at,
                    refunded_amount=Decimal("0.00"),
                ),
                Payment(
                    order_id=order_10088.id,
                    amount=Decimal("199.00"),
                    status=PaymentStatus.PAID.value,
                    paid_at=paid_at,
                    refunded_amount=Decimal("0.00"),
                ),
                Shipment(
                    order_id=order_10086.id,
                    status=ShipmentStatus.DELIVERED.value,
                    carrier="SF Express",
                    tracking_no="SF100860001",
                    shipped_at=now - timedelta(days=3),
                    delivered_at=delivered_at,
                ),
                Shipment(
                    order_id=order_10087.id,
                    status=ShipmentStatus.DELIVERED.value,
                    carrier="JD Logistics",
                    tracking_no="JD100870001",
                    shipped_at=now - timedelta(days=3),
                    delivered_at=delivered_at,
                ),
                Shipment(
                    order_id=order_10088.id,
                    status=ShipmentStatus.DELIVERED.value,
                    carrier="Digital Delivery",
                    tracking_no="DIGITAL100880001",
                    shipped_at=now - timedelta(days=1),
                    delivered_at=now - timedelta(days=1),
                ),
            ]
        )

        await db.commit()
        print("Demo data seeded successfully.")


if __name__ == "__main__":
    asyncio.run(seed_demo_data())