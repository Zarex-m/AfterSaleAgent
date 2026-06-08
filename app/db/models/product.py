from datetime import datetime
from decimal import Decimal
from enum import StrEnum

from sqlalchemy import Boolean, DateTime, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ProductCategory(StrEnum):
    CLOTHING = "clothing"
    ELECTRONICS = "electronics"
    FRESH_FOOD = "fresh_food"
    VIRTUAL_GOODS = "virtual_goods"
    BEAUTY = "beauty"
    HOME = "home"
    OTHER = "other"


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str] = mapped_column(
        String(50),
        default=ProductCategory.OTHER.value,
        nullable=False,
    )
    is_virtual: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_fresh: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )