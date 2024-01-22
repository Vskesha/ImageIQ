from unittest.mock import MagicMock
from src.conf import messages
from fastapi import status
from src.database.models import User
from typing import Optional


def test_create_user(client, user, monkeypatch):
    mock_send_email = MagicMock()
    monkeypatch.setattr("src.routes.auth.send_email", mock_send_email)
    response = client.post("/api/auth/signup", json=user)
    assert response.status_code == 201, response.text
    payload = response.json()
    assert payload["email"] == user.get("email")


def test_login_user_not_confirmed_email(client, user):
    response = client.post("/api/auth/login", data={"username": user.get("email"), "password": user.get("password")})
    assert response.status_code == 401, response.text
    payload = response.json()
    assert payload['detail'] == messages.EMAIL_NOT_CONFIRMED


def test_repeat_create_user(client, user, monkeypatch):
    mock_send_email = MagicMock()
    monkeypatch.setattr("src.routes.auth.send_email", mock_send_email)
    response = client.post("/api/auth/signup", json=user)
    assert response.status_code == 409, response.text
    payload = response.json()
    assert payload['detail'] == messages.ACCOUNT_EXISTS


def test_login_user(client, user, session):
    current_user: User = session.query(User).filter(User.email == user.get("email")).first()
    current_user.confirmed = True
    session.commit()
    response = client.post("/api/auth/login", data={"username": user.get("email"), "password": user.get("password")})
    payload = response.json()
    assert payload["token_type"] == "bearer"


def test_refresh_token_user(client, user, mock_ratelimiter, session):
    response = client.post(
        "/api/auth/login",
        data={"username": user.get("email"), "password": user.get("password")},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["token_type"] == "bearer"

    token = data["refresh_token"]
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get(
        "/api/auth/refresh_token",
        headers=headers,
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["token_type"] == "bearer"


def test_reset_password_ok(client, session, user, monkeypatch):
    mock_send_email = MagicMock()
    monkeypatch.setattr('src.routes.auth.send_email', mock_send_email)
    mock_send_reset_password = MagicMock()
    monkeypatch.setattr('src.routes.auth.send_reset_password', mock_send_reset_password)
    current_user: User = session.query(User).filter(User.email == user.get('email')).first()
    current_user.confirmed = True
    session.commit()
    response = client.post('api/auth/reset-password', json={'email': user.get('email')})
    assert response.status_code == status.HTTP_200_OK


def test_reset_password_check(client, session, user, monkeypatch):
    mock_send_email = MagicMock()
    monkeypatch.setattr('src.routes.auth.send_email', mock_send_email)
    mock_send_reset_password = MagicMock()
    monkeypatch.setattr('src.routes.auth.send_reset_password', mock_send_reset_password)
    current_user: User = session.query(User).filter(User.email == user.get('email')).first()
    current_user.confirmed = True
    session.commit()
    response = client.post('api/auth/reset-password', json={'email': user.get('email')})
    assert response.status_code == status.HTTP_200_OK


def test_logout_user(client, user_token, session):
    access_token = user_token['access_token']
    response = client.post("/api/auth/logout", headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200, response.text
    logged_out_user: Optional[User] = session.query(User).filter(User.email == "example2@example.com").first()
    assert logged_out_user.refresh_token is None


def test_login_user_wrong_password(client, user):
    response = client.post("/api/auth/login", data={"username": user.get("email"), "password": "password"})
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == messages.INVALID_PASSWORD


def test_login_user_wrong_email(client, user):
    response = client.post("/api/auth/login", data={"username": "username", "password": user.get("password")})
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == messages.INVALID_EMAIL