from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel


class ProductOut(BaseModel):
    id: str
    product_code: str
    product_name: str
    category: str
    unit: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class InventoryItemOut(BaseModel):
    id: str
    product_id: str
    warehouse: str
    quantity: int
    updated_at: datetime

    class Config:
        from_attributes = True


class CustomerOut(BaseModel):
    id: str
    customer_code: str
    customer_name: str
    level: str

    class Config:
        from_attributes = True


class OrderOut(BaseModel):
    id: str
    order_no: str
    customer_id: str
    product_id: str
    quantity: int
    status: str
    delivery_date: Optional[date]
    created_at: datetime

    class Config:
        from_attributes = True


class ProductionOrderOut(BaseModel):
    id: str
    order_no: str
    product_id: str
    planned_quantity: int
    completed_quantity: int
    status: str
    planned_date: Optional[date]
    completed_date: Optional[date]

    class Config:
        from_attributes = True


class PurchaseOrderOut(BaseModel):
    id: str
    purchase_no: str
    supplier: str
    product_id: str
    quantity: int
    status: str
    expected_date: Optional[date]

    class Config:
        from_attributes = True
