"""Script tạo Admin user."""

import asyncio
import sys
from pathlib import Path

# Thêm project root vào path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.config.settings import get_settings
from app.core.security import hash_password
from app.models.role import Role
from app.models.user import User

settings = get_settings()


async def create_admin():
    """Tạo admin user."""
    
    # Tạo engine và session
    engine = create_async_engine(settings.DATABASE_URL, echo=True)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        # 1. Kiểm tra admin đã tồn tại chưa
        result = await session.execute(
            select(User).where(User.email == "admin@example.com")
        )
        existing_admin = result.scalar_one_or_none()
        
        if existing_admin:
            print("❌ Admin user đã tồn tại!")
            print(f"   Email: {existing_admin.email}")
            print(f"   ID: {existing_admin.id}")
            return
        
        # 2. Lấy role admin hoặc super_admin
        result = await session.execute(
            select(Role).where(Role.code.in_(["super_admin", "admin"]))
        )
        admin_role = result.scalar_one_or_none()
        
        if not admin_role:
            print("❌ Không tìm thấy role admin/super_admin!")
            print("   Hãy chạy seed data trước.")
            return
        
        # 3. Tạo admin user
        admin_user = User(
            email="admin@example.com",
            hashed_password=hash_password("Admin@123"),
            full_name="System Administrator",
            is_active=True,
            is_verified=True,  # Admin không cần verify email
            role_id=admin_role.id
        )
        
        session.add(admin_user)
        await session.commit()
        await session.refresh(admin_user)
        
        print("✅ Admin user đã được tạo thành công!")
        print(f"   Email: {admin_user.email}")
        print("   Password: Admin@123")
        print(f"   Role: {admin_role.name}")
        print(f"   ID: {admin_user.id}")
        print("\n⚠️  Hãy đổi password sau khi đăng nhập!")
    
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(create_admin())