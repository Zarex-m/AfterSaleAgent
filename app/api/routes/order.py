from app.services.order_service import list_orders, get_order_by_no, get_order_items, get_payment_by_order_id, get_shipment_by_order_id 
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.db.models.order import Order, OrderItem
from app.db.models.payment import Payment
from app.db.models.shipment import Shipment
from app.schemas.order import OrderListItemResponse,OrderDetailResponse, OrderItemResponse, PaymentResponse, ShipmentResponse   
from app.api.dependencies import get_current_user

router = APIRouter(prefix="/orders", tags=["orders"])

@router.get("/",response_model=list[OrderListItemResponse])
async def list_orders_api(
    db:AsyncSession=Depends(get_db),
    current_user=Depends(get_current_user)
):
    return await list_orders(db)

@router.get("/{order_no}",response_model=OrderDetailResponse)
async def get_order_detail(
    order_no:str,
    db:AsyncSession=Depends(get_db),
    current_user=Depends(get_current_user),
):
    order=await get_order_by_no(db, order_no)
    if order is None:
        raise HTTPException(status_code=404,detail="Order not found")
    items=await get_order_items(db,order.id)
    return OrderDetailResponse.model_validate(
    {
        "id": order.id,
        "order_no": order.order_no,
        "customer_id": order.customer_id,
        "status": order.status,
        "total_amount": order.total_amount,
        "paid_at": order.paid_at,
        "created_at": order.created_at,
        "items": items,
    }
)

@router.get("/{order_no}/payment",response_model=PaymentResponse)
async def get_order_payment(
    order_no:str,
    db:AsyncSession=Depends(get_db),
    current_user=Depends(get_current_user),
):
    order=await get_order_by_no(db, order_no)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    payment=await get_payment_by_order_id(db, order.id)
    if payment is None:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment

@router.get("/{order_no}/shipment",response_model=ShipmentResponse)
async def get_order_shipment(
    order_no:str,
    db:AsyncSession=Depends(get_db),
    current_user=Depends(get_current_user),
):
    order=await get_order_by_no(db, order_no)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    shipment=await get_shipment_by_order_id(db, order.id)
    if shipment is None:
        raise HTTPException(status_code=404, detail="Shipment not found")
    return shipment
