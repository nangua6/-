from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db, get_current_user_payload
from app.models.business import Product, Inventory, Customer, Order, ProductionOrder, PurchaseOrder
from app.schemas.business import (
    ProductOut,
    InventoryItemOut,
    CustomerOut,
    OrderOut,
    ProductionOrderOut,
    PurchaseOrderOut,
)

router = APIRouter(prefix="/api", tags=["business"])


@router.get("/products", response_model=List[ProductOut])
async def list_products(q: Optional[str] = Query(default=None), _payload: dict = Depends(get_current_user_payload), db: AsyncSession = Depends(get_db)):
    stmt = select(Product)
    if q:
        stmt = stmt.where(or_(Product.product_code.ilike(f"%{q}%"), Product.product_name.ilike(f"%{q}%")))
    return (await db.execute(stmt.order_by(Product.created_at.desc()))).scalars().all()


@router.get("/products/{product_code}", response_model=ProductOut)
async def get_product(product_code: str, _payload: dict = Depends(get_current_user_payload), db: AsyncSession = Depends(get_db)):
    product = (await db.execute(select(Product).where(Product.product_code == product_code))).scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.get("/inventory", response_model=List[InventoryItemOut])
async def list_inventory(product_code: Optional[str] = Query(default=None), _payload: dict = Depends(get_current_user_payload), db: AsyncSession = Depends(get_db)):
    stmt = select(Inventory)
    if product_code:
        product = (await db.execute(select(Product).where(Product.product_code == product_code))).scalar_one_or_none()
        if not product:
            return []
        stmt = stmt.where(Inventory.product_id == product.id)
    return (await db.execute(stmt.order_by(Inventory.updated_at.desc()))).scalars().all()


@router.get("/customers/{customer_code}", response_model=CustomerOut)
async def get_customer(customer_code: str, _payload: dict = Depends(get_current_user_payload), db: AsyncSession = Depends(get_db)):
    customer = (await db.execute(select(Customer).where(Customer.customer_code == customer_code))).scalar_one_or_none()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer


@router.get("/orders/{order_no}", response_model=OrderOut)
async def get_order(order_no: str, _payload: dict = Depends(get_current_user_payload), db: AsyncSession = Depends(get_db)):
    order = (await db.execute(select(Order).where(Order.order_no == order_no))).scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@router.get("/production-orders/{order_no}", response_model=ProductionOrderOut)
async def get_production_order(order_no: str, _payload: dict = Depends(get_current_user_payload), db: AsyncSession = Depends(get_db)):
    production = (await db.execute(select(ProductionOrder).where(ProductionOrder.order_no == order_no))).scalar_one_or_none()
    if not production:
        raise HTTPException(status_code=404, detail="Production order not found")
    return production


@router.get("/purchase-orders/{purchase_no}", response_model=PurchaseOrderOut)
async def get_purchase_order(purchase_no: str, _payload: dict = Depends(get_current_user_payload), db: AsyncSession = Depends(get_db)):
    purchase = (await db.execute(select(PurchaseOrder).where(PurchaseOrder.purchase_no == purchase_no))).scalar_one_or_none()
    if not purchase:
        raise HTTPException(status_code=404, detail="Purchase order not found")
    return purchase
