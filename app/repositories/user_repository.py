# app/repositories/user_repository.py
# 
# Purpose: Database access layer for User operations.
# 
# Implementation details:
# - class UserRepository:
#     def __init__(self, db: AsyncSession)
#     async def get_by_id(user_id: str) -> User | None
#     async def get_by_email(email: str) -> User | None
#     async def create(user_data: UserCreate) -> User
#     async def update(user: User, update_data: UserUpdate) -> User
#     async def update_password(user: User, new_password: str) -> User
#     async def delete(user: User) -> None
