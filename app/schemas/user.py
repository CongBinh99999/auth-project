# app/schemas/user.py
# 
# Purpose: Pydantic schemas for User data transfer.
# 
# Implementation details:
# - UserBase: Common fields (email, full_name, is_active)
# - UserCreate(UserBase): Password field (input only)
# - UserUpdate(UserBase): All fields optional
# - UserResponse(UserBase): id, created_at, updated_at (attributes from ORM)
# - PasswordChange: old_password, new_password
