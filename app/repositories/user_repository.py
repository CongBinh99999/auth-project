from datetime import datetime, timezone
from uuid import UUID
from typing import Optional, List, Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update, and_, or_, func
from fastapi import Depends


from app.config.database import get_db
from app.models.user import User 
from app.schemas.user import UserCreate, UserUpdate


class UserRepository: 
    """Repository cho User entity - quản lý các thao tác CRUD với bảng users."""

    def __init__(self, db: AsyncSession): 
        """Khởi tạo repository với database session.
        
        Args:
            db: AsyncSession - Database session để thực hiện các thao tác.
        """
        self.db = db 

    
    async def get_by_id(self, user_id: UUID) -> Optional[User]: 
        """Lấy user theo ID.
        
        Args:
            user_id: UUID của user cần tìm.
            
        Returns:
            User nếu tìm thấy, None nếu không.
        """
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )

        return result.scalar_one_or_none()


    async def get_by_email(self, email: str) -> Optional[User]: 
        """Lấy user theo email.
        
        Args:
            email: Email của user cần tìm.
            
        Returns:
            User nếu tìm thấy, None nếu không.
        """
        result = await self.db.execute(
            select(User).where(User.email == email)
        )

        return result.scalar_one_or_none()


    async def create(self, **user_data) -> User: 
        """Tạo user mới.
        
        Args:
            **user_data: Dữ liệu user (email, hashed_password, role_id, ...).
            
        Returns:
            User đã được tạo.
        """
        user = User(**user_data)
        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)

        return user


    async def update(self, user: User, **update_data) -> User: 
        """Cập nhật thông tin user.
        
        Args:
            user: User object cần cập nhật.
            **update_data: Dữ liệu cần cập nhật.
            
        Returns:
            User đã được cập nhật.
        """
        for key, value in update_data.items(): 
            if hasattr(user, key): 
                setattr(user, key, value)
        
        user.updated_at = datetime.now(timezone.utc)
        await self.db.flush()
        await self.db.refresh(user)

        return user

    
    async def update_password(self, user: User, new_password: str) -> User:
        """Cập nhật mật khẩu user.
        
        Args:
            user: User object cần cập nhật.
            new_password: Mật khẩu mới đã được hash.
            
        Returns:
            User đã được cập nhật.
        """
        user.hashed_password = new_password
        user.updated_at = datetime.now(timezone.utc)
        
        await self.db.flush()
        await self.db.refresh(user)

        return user
    

    async def delete(self, user: User) -> None:
        """Xóa user khỏi database.
        
        Args:
            user: User object cần xóa.
        """
        self.db.delete(user)
        await self.db.flush()


def get_user_repository(
    db: Annotated[AsyncSession, Depends(get_db)]
) -> UserRepository: 
    """Dependency để inject UserRepository vào route handlers.
    
    Args:
        db: Database session từ dependency injection.
        
    Returns:
        UserRepository instance.
    """
    return UserRepository(db)


UserRepoDep = Annotated[UserRepository, Depends(get_user_repository)]