"""Token type enforcement - token sai loại phải bị từ chối."""

from uuid import uuid4

import pytest
from jose import JWTError

from app.core.security import create_token, decode_token
from app.utils.constants import TokenType


def _make(token_type: str) -> str:
    token, _, _ = create_token(subject=str(uuid4()), token_type=token_type)
    return token


def test_refresh_token_rejected_as_access():
    with pytest.raises(JWTError):
        decode_token(_make("refresh"), expected_type=TokenType.ACCESS)


def test_access_token_rejected_as_refresh():
    with pytest.raises(JWTError):
        decode_token(_make("access"), expected_type=TokenType.REFRESH)


def test_matching_type_accepted():
    assert decode_token(_make("access"), expected_type=TokenType.ACCESS).type == TokenType.ACCESS
    assert decode_token(_make("refresh"), expected_type=TokenType.REFRESH).type == TokenType.REFRESH


def test_no_expected_type_accepts_any():
    assert decode_token(_make("refresh")).type == TokenType.REFRESH
