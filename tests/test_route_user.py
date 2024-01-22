from unittest.mock import patch
from fastapi import status
from src.conf import messages


def test_read_users_me(client, access_token, mock_ratelimiter):
    response = client.get('api/users/me/')
    assert response.status_code == 401
    headers = {'Authorization': f'Bearer {access_token}'}
    response = client.get('api/users/me/', headers=headers)
    assert response.status_code == 200
    assert 'id' in response.json()
    assert 'username' in response.json()
    assert 'email' in response.json()
    assert 'role' in response.json()
    assert 'avatar' in response.json()


def test_update_avatar_user(client, access_token, monkeypatch, user, session, mock_ratelimiter):
    test_file = ("test.jpg", b"fakefile")
    with patch("src.services.cloud_image.CloudImage.generate_name_avatar", return_value="mock_public_id"), \
            patch("src.services.cloud_image.CloudImage.upload", return_value={"version": "mock_version"}), \
            patch("src.services.cloud_image.CloudImage.get_url_for_avatar", return_value="mock_url"), \
            patch("src.repository.users.update_avatar",
                  return_value={
                      "email": user.get("email"),
                      "avatar": "mock_url",
                      "id": 123,
                      "username": user.get("username"),
                      "role": "user",
                      "confirmed": "True",
                      "status_active": "True"}):
        response = client.patch(
            "/api/users/avatar",
            headers={"Authorization": f"Bearer {access_token}"},
            files={"file": test_file},
        )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["email"] == user.get("email")
    assert data["avatar"] == "mock_url"
    assert data["username"] == user.get("username")
    assert data["role"] == "user"
    assert data["id"] == 123


def test_ban_user_by_user(client, access_token, session, mock_ratelimiter):
    response = client.patch('api/users/ban_user/1/true')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    headers = {'Authorization': f'Bearer {access_token}'}

    response = client.patch('/api/users/ban_user/1/false', headers=headers)
    print('Помилка', response)
    assert response.status_code == status.HTTP_403_FORBIDDEN





