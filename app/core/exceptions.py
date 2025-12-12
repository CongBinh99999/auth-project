# app/core/exceptions.py
# 
# Purpose: Custom Exception definitions.
# 
# Implementation details:
# - class CredentialsException(HTTPException): 401
# - class InactiveUserException(HTTPException): 403
# - class UserAlreadyExistsException(HTTPException): 400
# - class UserNotFoundException(HTTPException): 404
# - class InvalidTokenException(HTTPException): 401
# - class TokenReuseException(HTTPException): 401
# - class PasswordMismatchException(HTTPException): 400
