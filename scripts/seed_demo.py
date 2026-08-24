from __future__ import annotations

import asyncio
from datetime import date, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.security import hash_password
from app.db.session import build_engine, build_session_factory
from app.models.business import Customer, Product, Inventory, Order, ProductionOrder, PurchaseOrder
from app.models.user import User

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "Admin123!"
USER_USERNAME = "operator"
USER_PASSWORD = "Operator123!"

PRODUCTS = [
    ("A001", "高强度螺丝 M8", "紧固件", "pcs"),
    ("A002", "高强度螺丝 M10", "紧固件", "pcs"),
    ("B001", "密封圈 DN50", "密封件", "pcs"),
    ("B002", "密封圈 DN80", "密封件", "pcs"),
    ("C001", "减速电机 0.75kW", "电机", "unit"),
    ("C002", "减速电机 1.5kW", "电机", "unit"),
    ("D001", "液压缸 63/35", "液压", "unit"),
    ("D002", "液压缸 80/45", "液压", "unit"),
    ("E001", "触摸屏 10寸", "电气", "unit"),
    ("E002", "触摸屏 15寸", "电气", "unit"),
]

CUSTOMERS = [
    ("CUS001", "华中重工", "VIP"),
    ("CUS002", "东方设备", "NORMAL"),
    ("CUS003", "南方制造", "NORMAL"),
    ("CUS004", "西部物流装备", "VIP"),
    ("CUS005", "北方自动化", "NORMAL"),
]

ORDERS = [
    ("SO20260001", "CUS001", "A001", 5000, "IN_PRODUCTION", date.today() + timedelta(days=3)),
    ("SO20260002", "CUS002", "B001", 800, "OPEN", date.today() + timedelta(days=12)),
    ("SO20260003", "CUS003", "C001", 120, "IN_PRODUCTION", date.today() + timedelta(days=6)),
    ("SO20260004", "CUS004", "D002", 60, "COMPLETED", date.today() + timedelta(days=15)),
    ("SO20260005", "CUS005", "E001", 300, "OPEN", date.today() + timedelta(days=20)),
]

PURCHASES = [
    ("PO20260001", "供应商甲", "A001", 20000, "CONFIRMED", date.today() + timedelta(days=2)),
    ("PO20260002", "供应商乙", "B001", 4000, "OPEN", date.today() + timedelta(days=7)),
    ("PO20260003", "供应商丙", "C001", 200, "CONFIRMED", date.today() + timedelta(days=5)),
    ("PO20260004", "供应商丁", "D002", 100, "RECEIVED", date.today() + timedelta(days=10)),
    ("PO20260005", "供应商戊", "E001", 500, "OPEN", date.today() + timedelta(days=9)),
]


async def main() -> None:
    settings = get_settings()
    engine = build_engine(settings)
    factory = build_session_factory(engine)

    async with factory() as session:  # type: AsyncSession
        admin = (await session.execute(select(User).where(User.username == ADMIN_USERNAME))).scalar_one_or_none()
        if not admin:
            session.add(User(username=ADMIN_USERNAME, password_hash=hash_password(ADMIN_PASSWORD), role="ADMIN"))

        user = (await session.execute(select(User).where(User.username == USER_USERNAME))).scalar_one_or_none()
        if not user:
            session.add(User(username=USER_USERNAME, password_hash=hash_password(USER_PASSWORD), role="USER"))

        code_to_product = {}
        for code, name, category, unit in PRODUCTS:
            product = (await session.execute(select(Product).where(Product.product_code == code))).scalar_one_or_none()
            if not product:
                product = Product(product_code=code, product_name=name, category=category, unit=unit)
                session.add(product)
            code_to_product[code] = product

        for code, name, level in CUSTOMERS:
            customer = (await session.execute(select(Customer).where(Customer.customer_code == code))).scalar_one_or_none()
            if not customer:
                session.add(Customer(customer_code=code, customer_name=name, level=level))

        await session.flush()

        for code, product in code_to_product.items():
            exists = (await session.execute(select(Inventory).where(Inventory.product_id == product.id))).scalar_one_or_none()
            if not exists:
                session.add(Inventory(product_id=product.id, warehouse="MAIN", quantity=1000))

        customers = {c.customer_code: c for c in (await session.execute(select(Customer))).scalars().all()}

        for order_no, customer_code, product_code, quantity, status, delivery_date in ORDERS:
            exists = (await session.execute(select(Order).where(Order.order_no == order_no))).scalar_one_or_none()
            if not exists:
                session.add(Order(order_no=order_no, customer_id=customers[customer_code].id, product_id=code_to_product[product_code].id, quantity=quantity, status=status, delivery_date=delivery_date))

        for order_no, customer_code, product_code, quantity, status, delivery_date in ORDERS:
            exists = (await session.execute(select(ProductionOrder).where(ProductionOrder.order_no == order_no))).scalar_one_or_none()
            if not exists:
                completed = quantity if status == "COMPLETED" else int(quantity * 0.6) if status == "IN_PRODUCTION" else 0
                session.add(ProductionOrder(order_no=order_no, product_id=code_to_product[product_code].id, planned_quantity=quantity, completed_quantity=completed, status=status, planned_date=delivery_date, completed_date=delivery_date if status == "COMPLETED" else None))

        for purchase_no, supplier, product_code, quantity, status, expected_date in PURCHASES:
            exists = (await session.execute(select(PurchaseOrder).where(PurchaseOrder.purchase_no == purchase_no))).scalar_one_or_none()
            if not exists:
                session.add(PurchaseOrder(purchase_no=purchase_no, supplier=supplier, product_id=code_to_product[product_code].id, quantity=quantity, status=status, expected_date=expected_date))

        await session.commit()

    await engine.dispose()
    print("Seed data ready.")


if __name__ == "__main__":
    asyncio.run(main())
