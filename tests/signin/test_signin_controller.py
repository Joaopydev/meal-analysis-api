import pytest
from unittest.mock import Mock, AsyncMock

from src.controllers.signin import SigninController


@pytest.mark.asyncio
async def test_signin_controller_invalid_email():
    request_body = {
        "email": "invalid-email",
        "password": "password",
    }

    controller = SigninController(
        user_repository=Mock(),
        hashed_service=Mock(),
    )
    response = await controller.handle(request_body)
    assert response["statusCode"] == 400
    assert response["body"]["errors"][0]["type"] == "value_error"

@pytest.mark.asyncio
async def test_signin_controller_invalid_credentials():
    request_body = {
        "email": "joao@gmail.com",
        "password": "password",
    }

    user_repository_mock = AsyncMock()
    user_repository_mock.get_user_by_email.return_value = None
    controller = SigninController(
        user_repository=user_repository_mock,
        hashed_service=Mock()
    )

    result = await controller.handle(body=request_body)

    user_repository_mock.get_user_by_email.assert_called_once_with(email="joao@gmail.com")
    assert result["statusCode"] == 401
    assert result["body"]["error"] == "Invalid Credentials."


@pytest.mark.asyncio
async def test_signin_controller_ok():
    request_body = {
        "email": "test@gmail.com",
        "password": "password",
    }

    user_repository_mock = AsyncMock()
    user_repository_mock.get_user_by_email.return_value = Mock(
        email="test@gmail.com",
        password="password"
    )
    hashed_service_mock = Mock()
    hashed_service_mock.verify_password.return_value = True

    controller = SigninController(
        user_repository=user_repository_mock,
        hashed_service=hashed_service_mock
    )

    result = await controller.handle(body=request_body)

    user_repository_mock.get_user_by_email.assert_called_once_with(email="test@gmail.com")
    hashed_service_mock.verify_password.assert_called_once_with(
        password="password",
        hashed_password="password"
    )
    assert result["statusCode"] == 200
    assert "access_token" in result["body"]