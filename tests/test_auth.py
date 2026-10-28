import pytest

base_path = "api/v1/auth"

async def user_register_success(client):
    response = await client.post(
        f"{base_path}/register",
        json={
            "email": "test@example.ru",
            "password": "TestPassword123",
        }
    )

    assert response.status_code == 201

    return response


@pytest.mark.asyncio
async def test_register_user_success(client):

    response_create_user = await user_register_success(client)

    data = response_create_user.json()

    assert data["email"] == "test@example.ru"
    assert "role" in data
    assert "id" in data
    assert "password_hash" not in data
    assert "created_at" not in data


@pytest.mark.asyncio
async def test_register_duplicate_email(client):
    payload = {
        "email": "test@example.ru",
        "password": "TestPassword123",
    }

    first_response = await client.post(
        f"{base_path}/register",
        json=payload,
    )

    second_response = await client.post(
        f"{base_path}/register",
        json=payload,
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 400
    assert second_response.json()["detail"] == "Email already registered"


@pytest.mark.asyncio
async def test_register_invalid_email(client):

    response = await client.post(
        f"{base_path}/register",
        json={
            "email": "not-email",
            "password": "TestPassword123",
        },
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_authenticate_user_success(client):

    response_create_user = await user_register_success(client)

    data_register = response_create_user.json()

    assert data_register["email"] == "test@example.ru"
    assert "role" in data_register
    assert "id" in data_register
    assert "password_hash" not in data_register
    assert "created_at" not in data_register

    response_login = await client.post(
        f"{base_path}/login",
        data={
            "username": data_register["email"],
            "password": "TestPassword123",
        }
    )

    assert response_login.status_code == 200

    data_login = response_login.json()

    assert "access_token" in data_login
    assert data_login["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_authenticate_user_invalid_password(client):

    response_create_user = await user_register_success(client)

    data_register = response_create_user.json()

    assert data_register["email"] == "test@example.ru"
    assert "role" in data_register
    assert "id" in data_register
    assert "password_hash" not in data_register
    assert "created_at" not in data_register

    response_login = await client.post(
        f"{base_path}/login",
        data={
            "username": data_register["email"],
            "password": "123TestPassword",
        }
    )

    assert response_login.status_code == 401