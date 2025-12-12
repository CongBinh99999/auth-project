# app/schemas/role.py
# 
# Purpose: Pydantic schemas for Role data transfer (RBAC).
# 
# Implementation details:
# - RoleBase: name, code, description
# - RoleCreate(RoleBase): is_default, is_system
# - RoleUpdate: all fields optional
# - RoleResponse(RoleBase): id, is_default, is_system, created_at, updated_at
# - RoleWithPermissions(RoleResponse): permissions list
# 
# - PermissionBase: name, code, description, module
# - PermissionCreate(PermissionBase): pass
# - PermissionResponse(PermissionBase): id, created_at
