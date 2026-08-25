from __future__ import annotations

import asyncio
import sys
from pathlib import Path
from datetime import date, timedelta

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.security import hash_password
from app.db.session import build_engine, build_session_factory
from app.db.base import Base
from app.models.business import Customer, Product, Inventory, Order, ProductionOrder, PurchaseOrder
from app.models.user import User
from app.models.session import ConversationSession  # noqa: F401
from app.models.message import Message  # noqa: F401
from app.models.trace import AgentTrace, ToolTrace, RetrievalTrace  # noqa: F401
from app.models.business import Document, DocumentChunk, Embedding  # noqa: F401

# ── 用户 ──────────────────────────────────────────────
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "Admin123!"
USER_USERNAME = "operator"
USER_PASSWORD = "Operator123!"

# ── 格力空调零部件产品 ─────────────────────────────────
PRODUCTS = [
    ("GREE-CMP-001", "凌达压缩机 QXA-B113N030A (1.5匹)", "压缩机", "台"),
    ("GREE-CMP-002", "凌达压缩机 QXA-B165N050A (3匹)", "压缩机", "台"),
    ("GREE-CMP-003", "凌达压缩机 QXA-B220N070A (5匹)", "压缩机", "台"),
    ("GREE-EVP-001", "蒸发器 Φ7内螺纹铜管 (1.5匹)", "换热器", "套"),
    ("GREE-EVP-002", "蒸发器 Φ9.52内螺纹铜管 (3匹)", "换热器", "套"),
    ("GREE-CND-001", "冷凝器 双排Φ7亲水铝箔 (1.5匹)", "换热器", "套"),
    ("GREE-CND-002", "冷凝器 三排Φ9.52亲水铝箔 (3匹)", "换热器", "套"),
    ("GREE-FAN-001", "贯流风轮 Φ98×630mm (挂机)", "风机", "个"),
    ("GREE-FAN-002", "离心风轮 Φ280×150mm (柜机)", "风机", "个"),
    ("GREE-FAN-003", "室外轴流风扇 Φ450mm", "风机", "个"),
    ("GREE-PCB-001", "主控板 GMV-N300 (变频挂机)", "电控", "块"),
    ("GREE-PCB-002", "主控板 GMV-N500 (变频柜机)", "电控", "块"),
    ("GREE-PCB-003", "室外机驱动板 IPM-3P (3匹)", "电控", "块"),
    ("GREE-PCB-004", "WiFi模组 GR-WiFi-V3", "电控", "块"),
    ("GREE-VAL-001", "电子膨胀阀 DPF-1.6C (R32)", "阀件", "个"),
    ("GREE-VAL-002", "四通换向阀 SHF-4-32 (R32)", "阀件", "个"),
    ("GREE-VAL-003", "截止阀 1/4\" 铜阀", "阀件", "个"),
    ("GREE-FLT-001", "HEPA滤网 H13 挂机通用", "过滤网", "片"),
    ("GREE-FLT-002", "活性炭除甲醛滤网 挂机", "过滤网", "片"),
    ("GREE-SNR-001", "温度传感器 NTC 10KΩ 管温", "传感器", "个"),
    ("GREE-SNR-002", "压力传感器 0-5MPa R32", "传感器", "个"),
    ("GREE-MTR-001", "直流无刷电机 30W 挂机室内", "电机", "台"),
    ("GREE-MTR-002", "直流无刷电机 75W 柜机室内", "电机", "台"),
    ("GREE-HSG-001", "ABS塑料外壳 白色 挂机面板", "结构件", "套"),
    ("GREE-HSG-002", "钣金外壳 室外机底壳", "结构件", "套"),
    ("GREE-PKG-001", "包装纸箱 挂机标准", "包装", "个"),
    ("GREE-PKG-002", "EPS泡沫内衬 挂机", "包装", "套"),
    ("GREE-RFG-001", "R32环保冷媒 10kg/瓶", "冷媒", "瓶"),
    ("GREE-PIP-001", "紫铜管 Φ9.52×0.7mm 盘管", "管路", "米"),
    ("GREE-PIP-002", "紫铜管 Φ12.7×0.8mm 盘管", "管路", "米"),
]

CUSTOMERS = [
    ("GZ-001", "广州格力销售公司", "VIP"),
    ("SZ-002", "深圳格力旗舰店", "VIP"),
    ("BJ-003", "北京盛世恒通格力专卖", "VIP"),
    ("SH-004", "上海申菱电器", "NORMAL"),
    ("CD-005", "成都格力西南总代", "VIP"),
    ("WH-006", "武汉格力经销商", "NORMAL"),
    ("HZ-007", "杭州格力体验馆", "NORMAL"),
    ("NJ-008", "南京格力服务中心", "NORMAL"),
    ("XA-009", "西安格力西北代理", "NORMAL"),
    ("CS-010", "长沙格力旗舰店", "NORMAL"),
]

ORDERS = [
    ("SO20260801", "GZ-001", "GREE-CMP-001", 2000, "IN_PRODUCTION", date(2026, 9, 5)),
    ("SO20260802", "GZ-001", "GREE-PCB-001", 3000, "IN_PRODUCTION", date(2026, 9, 10)),
    ("SO20260803", "SZ-002", "GREE-EVP-001", 1500, "OPEN", date(2026, 9, 15)),
    ("SO20260804", "BJ-003", "GREE-CMP-002", 800, "IN_PRODUCTION", date(2026, 9, 8)),
    ("SO20260805", "BJ-003", "GREE-VAL-001", 5000, "OPEN", date(2026, 9, 20)),
    ("SO20260806", "SH-004", "GREE-FAN-001", 4000, "COMPLETED", date(2026, 8, 30)),
    ("SO20260807", "CD-005", "GREE-PCB-003", 1200, "IN_PRODUCTION", date(2026, 9, 12)),
    ("SO20260808", "CD-005", "GREE-CND-001", 1800, "OPEN", date(2026, 9, 18)),
    ("SO20260809", "WH-006", "GREE-MTR-001", 6000, "IN_PRODUCTION", date(2026, 9, 6)),
    ("SO20260810", "HZ-007", "GREE-FLT-001", 10000, "COMPLETED", date(2026, 8, 25)),
    ("SO20260811", "NJ-008", "GREE-SNR-001", 8000, "OPEN", date(2026, 9, 22)),
    ("SO20260812", "XA-009", "GREE-CMP-003", 500, "IN_PRODUCTION", date(2026, 9, 14)),
    ("SO20260813", "CS-010", "GREE-VAL-002", 3000, "OPEN", date(2026, 9, 25)),
    ("SO20260814", "GZ-001", "GREE-HSG-001", 2500, "IN_PRODUCTION", date(2026, 9, 9)),
    ("SO20260815", "SZ-002", "GREE-RFG-001", 500, "OPEN", date(2026, 9, 28)),
]

PURCHASES = [
    ("PO20260801", "珠海凌达压缩机有限公司", "GREE-CMP-001", 5000, "CONFIRMED", date(2026, 9, 1)),
    ("PO20260802", "珠海凌达压缩机有限公司", "GREE-CMP-002", 1500, "CONFIRMED", date(2026, 9, 3)),
    ("PO20260803", "珠海凌达压缩机有限公司", "GREE-CMP-003", 800, "OPEN", date(2026, 9, 10)),
    ("PO20260804", "佛山华鹭制冷配件", "GREE-EVP-001", 3000, "CONFIRMED", date(2026, 9, 5)),
    ("PO20260805", "佛山华鹭制冷配件", "GREE-CND-001", 3000, "OPEN", date(2026, 9, 12)),
    ("PO20260806", "中山大洋电机股份", "GREE-MTR-001", 10000, "CONFIRMED", date(2026, 8, 28)),
    ("PO20260807", "中山大洋电机股份", "GREE-MTR-002", 3000, "RECEIVED", date(2026, 8, 20)),
    ("PO20260808", "珠海格力电子元件", "GREE-PCB-001", 5000, "CONFIRMED", date(2026, 9, 2)),
    ("PO20260809", "珠海格力电子元件", "GREE-PCB-002", 2000, "OPEN", date(2026, 9, 8)),
    ("PO20260810", "珠海格力电子元件", "GREE-PCB-003", 2000, "IN_PRODUCTION", date(2026, 9, 6)),
    ("PO20260811", "浙江三花智能控制", "GREE-VAL-001", 8000, "CONFIRMED", date(2026, 9, 4)),
    ("PO20260812", "浙江三花智能控制", "GREE-VAL-002", 5000, "OPEN", date(2026, 9, 15)),
    ("PO20260813", "广东美芝精密部件", "GREE-FAN-001", 6000, "CONFIRMED", date(2026, 9, 1)),
    ("PO20260814", "广东美芝精密部件", "GREE-FAN-002", 2000, "RECEIVED", date(2026, 8, 22)),
    ("PO20260815", "深圳安培盛科技", "GREE-SNR-001", 15000, "CONFIRMED", date(2026, 9, 7)),
    ("PO20260816", "顺德科龙滤网厂", "GREE-FLT-001", 20000, "CONFIRMED", date(2026, 8, 30)),
    ("PO20260817", "顺德科龙滤网厂", "GREE-FLT-002", 8000, "OPEN", date(2026, 9, 18)),
    ("PO20260818", "山东东岳化工", "GREE-RFG-001", 1000, "CONFIRMED", date(2026, 9, 3)),
    ("PO20260819", "海亮集团铜加工", "GREE-PIP-001", 50000, "CONFIRMED", date(2026, 9, 1)),
    ("PO20260820", "海亮集团铜加工", "GREE-PIP-002", 30000, "OPEN", date(2026, 9, 10)),
]


async def main() -> None:
    settings = get_settings()
    engine = build_engine(settings)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    factory = build_session_factory(engine)

    async with factory() as session:
        # 用户
        admin = (await session.execute(select(User).where(User.username == ADMIN_USERNAME))).scalar_one_or_none()
        if not admin:
            session.add(User(username=ADMIN_USERNAME, password_hash=hash_password(ADMIN_PASSWORD), role="ADMIN"))
        user = (await session.execute(select(User).where(User.username == USER_USERNAME))).scalar_one_or_none()
        if not user:
            session.add(User(username=USER_USERNAME, password_hash=hash_password(USER_PASSWORD), role="USER"))

        # 产品
        code_to_product = {}
        for code, name, category, unit in PRODUCTS:
            product = (await session.execute(select(Product).where(Product.product_code == code))).scalar_one_or_none()
            if not product:
                product = Product(product_code=code, product_name=name, category=category, unit=unit)
                session.add(product)
            code_to_product[code] = product

        # 客户
        for code, name, level in CUSTOMERS:
            customer = (await session.execute(select(Customer).where(Customer.customer_code == code))).scalar_one_or_none()
            if not customer:
                session.add(Customer(customer_code=code, customer_name=name, level=level))
        await session.flush()

        # 库存
        inventory_map = {
            "GREE-CMP-001": 3200, "GREE-CMP-002": 1100, "GREE-CMP-003": 450,
            "GREE-EVP-001": 2800, "GREE-EVP-002": 900,
            "GREE-CND-001": 2600, "GREE-CND-002": 750,
            "GREE-FAN-001": 5500, "GREE-FAN-002": 1800, "GREE-FAN-003": 3200,
            "GREE-PCB-001": 4100, "GREE-PCB-002": 1600, "GREE-PCB-003": 1400, "GREE-PCB-004": 6000,
            "GREE-VAL-001": 7200, "GREE-VAL-002": 4300, "GREE-VAL-003": 9500,
            "GREE-FLT-001": 18000, "GREE-FLT-002": 6500,
            "GREE-SNR-001": 12000, "GREE-SNR-002": 3800,
            "GREE-MTR-001": 8500, "GREE-MTR-002": 2700,
            "GREE-HSG-001": 3500, "GREE-HSG-002": 2200,
            "GREE-PKG-001": 4500, "GREE-PKG-002": 4200,
            "GREE-RFG-001": 800,
            "GREE-PIP-001": 42000, "GREE-PIP-002": 28000,
        }
        for code, product in code_to_product.items():
            exists = (await session.execute(select(Inventory).where(Inventory.product_id == product.id))).scalar_one_or_none()
            if not exists:
                session.add(Inventory(product_id=product.id, warehouse="珠海金湾仓", quantity=inventory_map.get(code, 1000)))

        customers = {c.customer_code: c for c in (await session.execute(select(Customer))).scalars().all()}

        # 销售订单
        for order_no, customer_code, product_code, quantity, status, delivery_date in ORDERS:
            exists = (await session.execute(select(Order).where(Order.order_no == order_no))).scalar_one_or_none()
            if not exists:
                session.add(Order(order_no=order_no, customer_id=customers[customer_code].id, product_id=code_to_product[product_code].id, quantity=quantity, status=status, delivery_date=delivery_date))

        # 生产工单
        for order_no, customer_code, product_code, quantity, status, delivery_date in ORDERS:
            exists = (await session.execute(select(ProductionOrder).where(ProductionOrder.order_no == order_no))).scalar_one_or_none()
            if not exists:
                completed = quantity if status == "COMPLETED" else int(quantity * 0.6) if status == "IN_PRODUCTION" else 0
                session.add(ProductionOrder(order_no=order_no, product_id=code_to_product[product_code].id, planned_quantity=quantity, completed_quantity=completed, status=status, planned_date=delivery_date, completed_date=delivery_date if status == "COMPLETED" else None))

        # 采购订单
        for purchase_no, supplier, product_code, quantity, status, expected_date in PURCHASES:
            exists = (await session.execute(select(PurchaseOrder).where(PurchaseOrder.purchase_no == purchase_no))).scalar_one_or_none()
            if not exists:
                session.add(PurchaseOrder(purchase_no=purchase_no, supplier=supplier, product_id=code_to_product[product_code].id, quantity=quantity, status=status, expected_date=expected_date))

        await session.commit()

        # 知识库文档
        from app.services.knowledge_service import import_document_from_path
        knowledge_dir = Path(__file__).resolve().parents[1] / "data" / "knowledge"
        for md_file in knowledge_dir.glob("*.md"):
            result = await import_document_from_path(session, md_file, title=md_file.stem)
            print(f"   📚 {md_file.name}: {result.get('status', 'unknown')}")

    await engine.dispose()
    print("✅ 格力空调零部件演示数据导入完成")
    print(f"   - 产品: {len(PRODUCTS)} 个")
    print(f"   - 客户: {len(CUSTOMERS)} 个")
    print(f"   - 销售订单: {len(ORDERS)} 个")
    print(f"   - 采购订单: {len(PURCHASES)} 个")


if __name__ == "__main__":
    asyncio.run(main())
