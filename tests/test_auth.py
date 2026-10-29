import pytest

import jwt
from datetime import datetime, timedelta, timezone

from shopapi.core.config import settings

base_path = "api/v1/auth"

async def user_register_success(client):

    response = await client.post(
        url=f"{base_path}/register",
        json={
            "email": "test@example.ru",
            "password": "!TestPassword123",
        }
    )

    assert response.status_code == 201

    data = response.json()

    assert data["email"] == "test@example.ru"
    assert "role" in data
    assert "id" in data
    assert "password_hash" not in data
    assert "created_at" not in data

    return response

async def user_login_success(client):
    await user_register_success(client)

    response_login = await client.post(
        url=f"{base_path}/login",
        data={
            "username": "test@example.ru",
            "password": "!TestPassword123",
        }
    )

    assert response_login.status_code == 200

    return response_login


@pytest.mark.asyncio
async def test_register_user_success(client):

    await user_register_success(client)


@pytest.mark.asyncio
async def test_register_duplicate_email(client):
    payload = {
        "email": "test@example.ru",
        "password": "!TestPassword123",
    }

    first_response = await client.post(
        url=f"{base_path}/register",
        json=payload,
    )

    second_response = await client.post(
        url=f"{base_path}/register",
        json=payload,
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 400
    assert second_response.json()["detail"] == "Email already registered"


@pytest.mark.asyncio
async def test_register_invalid_email(client):

    response = await client.post(
        url=f"{base_path}/register",
        json={
            "email": "not-email",
            "password": "!TestPassword123",
        },
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_authenticate_user_success(client):

    response_create_user = await user_register_success(client)

    data_register = response_create_user.json()

    response_login = await client.post(
        url=f"{base_path}/login",
        data={
            "username": data_register["email"],
            "password": "!TestPassword123",
        }
    )

    assert response_login.status_code == 200

    data_login = response_login.json()

    assert "access_token" in data_login
    assert data_login["token_type"] == "bearer"

    return response_login


@pytest.mark.asyncio
async def test_authenticate_user_invalid_password(client):

    response_create_user = await user_register_success(client)

    data_register = response_create_user.json()

    response_login = await client.post(
        url=f"{base_path}/login",
        data={
            "username": data_register["email"],
            "password": "123TestPassword!",
        }
    )

    assert response_login.status_code == 401

@pytest.mark.negative
async def test_register_user_empty_password(client):

    response = await client.post(
        url=f"{base_path}/register",
        json={
            "email": "test@example.ru",
            "password": "",
        }
    )

    assert response.status_code == 400


@pytest.mark.negative
async def test_register_user_non_special_symbol_password(client):

    response = await client.post(
        url=f"{base_path}/register",
        json={
            "email": "test@example.ru",
            "password": "TestPassword123",
        }
    )

    assert response.status_code == 400


@pytest.mark.negative
async def test_register_user_non_capital_letter_password(client):

    response = await client.post(
        url=f"{base_path}/register",
        json={
            "email": "test@example.ru",
            "password": "!testpassword123",
        }
    )

    assert response.status_code == 400


@pytest.mark.asyncio
async def test_auth_me_success(client):

    response_login = await user_login_success(client)
    access_token = response_login.json()["access_token"]

    response = await client.get(
        url=f"{base_path}/me",
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    assert response.status_code == 200

    result = response.json()

    assert result["email"] == "test@example.ru"
    assert "id" in result
    assert "role" in result
    assert "password_hash" not in result


@pytest.mark.negative
async def test_auth_me_no_token(client):

    response = await client.get(
        url=f"{base_path}/me"
    )

    assert response.status_code == 401

    result = response.json()

    assert "detail" in result
    assert result["detail"] == "Not authenticated"


@pytest.mark.negative
async def test_auth_me_invalid_token(client):

    response = await client.get(
        url=f"{base_path}/me",
        headers={
            "Authorization": f"Bearer invalid token"
        }
    )

    assert response.status_code == 401

    result = response.json()

    assert "detail" in result
    assert result["detail"] == "Could not validate token"


@pytest.mark.negative
async def test_auth_me_expired_token(client):
    expired_payload = {
        "sub": "test@example.ru",
        "exp": datetime.now(timezone.utc) - timedelta(minutes=10)
    }

    access_token = jwt.encode(
        expired_payload,
        settings.secret_key,
        algorithm=settings.algorithm
    )

    response = await client.get(
        url=f"{base_path}/me",
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate token"


@pytest.mark.negative
async def test_auth_me_no_email_token(client):

    payload = {
        "exp": datetime.now(timezone.utc) + timedelta(minutes=10)
    }

    access_token = jwt.encode(
        payload,
        settings.secret_key,
        algorithm=settings.algorithm
    )

    response = await client.get(
        url=f"{base_path}/me",
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate token"


@pytest.mark.negative
async def test_auth_me_unknown_user_token(client):
    payload = {
        "sub": "test@example.ru",
        "exp": datetime.now(timezone.utc) + timedelta(minutes=10)
    }

    access_token = jwt.encode(
        payload,
        settings.secret_key,
        algorithm=settings.algorithm
    )

    response = await client.get(
        url=f"{base_path}/me",
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate token"


