from unittest.mock import patch, AsyncMock, MagicMock
import io
import unittest.mock as um
from src.conf import messages
from src.services.auth import auth_service
from src.database.models import User, Image


def test_create_image_by_admin(client, session, admin, admin_token, image, monkeypatch, mock_ratelimiter):
    with patch.object(auth_service.token_manager, 'r') as redis_mock:
        redis_mock.get.return_value = None
        mock_public_id = MagicMock()
        monkeypatch.setattr('src.services.cloud_image.CloudImage.generate_name_image', mock_public_id)
        mock_r = MagicMock()
        monkeypatch.setattr('src.services.cloud_image.CloudImage.image_upload', mock_r)
        mock_src_url = MagicMock()
        mock_src_url.return_value = 'some url'
        monkeypatch.setattr('src.services.cloud_image.CloudImage.get_url_for_image', mock_src_url)
        current_user = session.query(User).filter_by(email=admin.get('email')).first()
        session.expunge(current_user)

        with um.patch('builtins.open', um.mock_open(read_data='test')) as mock_file:
            response = client.post(
                '/api/images/',
                params={'description': image['description'], 'tags': image['tags']},

                files={'file': ('filename', open(mock_file, 'rb'), 'image/jpeg')},
                headers={'Authorization': f'''Bearer {admin_token['access_token']}'''}
            )
        assert response.status_code == 200, response.text
        data = response.json()
        assert data['description'] == image['description']
        assert data['tags'][0]['name'] == image['tags'].split()[0]
        assert data['user_id'] == current_user.id
        assert 'id' in data


def test_create_image_by_user(client, session, user, user_token, image, monkeypatch, mock_ratelimiter):
    with patch.object(auth_service.token_manager, 'r') as redis_mock:
        redis_mock.get.return_value = None
        mock_public_id = MagicMock()
        monkeypatch.setattr('src.services.cloud_image.CloudImage.generate_name_image', mock_public_id)
        mock_r = MagicMock()
        monkeypatch.setattr('src.services.cloud_image.CloudImage.image_upload', mock_r)
        mock_src_url = MagicMock()
        mock_src_url.return_value = 'some url'
        monkeypatch.setattr('src.services.cloud_image.CloudImage.get_url_for_image', mock_src_url)
        current_user = session.query(User).filter_by(email=user.get('email')).first()
        session.expunge(current_user)

        with um.patch('builtins.open', um.mock_open(read_data='test')) as mock_file:
            response = client.post(
                '/api/images/',
                params={'description': image['description'], 'tags': image['tags']},

                files={'file': ('filename', open(mock_file, 'rb'), 'image/jpeg')},
                headers={'Authorization': f'''Bearer {user_token['access_token']}'''}
            )
        assert response.status_code == 200, response.text
        data = response.json()
        assert data['description'] == image['description']
        assert data['tags'][0]['name'] == image['tags'].split()[0]
        assert data['user_id'] == current_user.id
        assert 'id' in data

def test_get_image(client, session, user_token, image, monkeypatch, mock_ratelimiter):
    with patch.object(auth_service.token_manager, 'r') as redis_mock:
        redis_mock.get.return_value = None
        response = client.get(
            '/api/images/1',
            headers={'Authorization': f'''Bearer {user_token['access_token']}'''}
        )
        data = response.json()
        assert response.status_code == 200, response.text
        assert type(data) == dict
        assert data['description'] == image['description']
        assert 'id' in data


def test_image_no_such_image(client, session, user_token, image, monkeypatch, mock_ratelimiter):
    with patch.object(auth_service.token_manager, 'r') as redis_mock:
        redis_mock.get.return_value = None
        response = client.get(
                    '/api/images/999',
                    headers={'Authorization': f'''Bearer {user_token['access_token']}'''}
                )
        data = response.json()
        assert response.status_code == 404, response.text
        assert data['detail'] == messages.MSC404_IMAGE_NOT_FOUND


def test_image_qrcode(client, session, user, user_token, image, monkeypatch, mock_ratelimiter):
    with patch.object(auth_service.token_manager, 'r') as redis_mock:
        redis_mock.get.return_value = None

        user = session.query(User).filter_by(email=user.get('email')).first()
        test_image = session.query(Image).filter_by(user_id=user.id).first()

        response = client.get(
            f'/api/images/qrcode/{test_image.id}',
            headers={'Authorization': f'''Bearer {user_token['access_token']}'''}
        )

        assert response.status_code == 200
        assert response.headers['Content-Type'] == 'image/png'
        assert type(response._content) is bytes


def test_get_image_by_tag_name(client, session, user_token, image, monkeypatch, mock_ratelimiter):
    with patch.object(auth_service.token_manager, 'r') as redis_mock:
        redis_mock.get.return_value = None

        response = client.get(
                              f'''api//images/search_bytag/{image['tags'].split()[0]}''',
                              params={'sort_direction': 'asc'},
                              headers={'Authorization': f'''Bearer {user_token['access_token']}'''}
                              )
        data = response.json()
        assert response.status_code == 200, response.text
        assert type(data) == list
        assert data[0]['description'] == image['description']
        assert 'id' in data[0]


def test_get_image_by_tag_name_no_tags(client, session, user_token, image, monkeypatch, mock_ratelimiter):
    with patch.object(auth_service.token_manager, 'r') as redis_mock:
        redis_mock.get.return_value = None

    response = client.get(
            f'api//images/search_bytag/no_tag',
            params={'sort_direction': 'asc'},
            headers={'Authorization': f'''Bearer {user_token['access_token']}'''}
        )
    data = response.json()
    assert response.status_code == 404, response.text
    assert data['detail'] == messages.MSC404_TAG_NOT_FOUND


def test_transforme_image(client, session, user, user_token, image, monkeypatch, mock_ratelimiter):
    with patch.object(auth_service.token_manager, 'r') as redis_mock:
        redis_mock.get.return_value = None
        user = session.query(User).filter_by(email=user.get('email')).first()
        test_image = session.query(Image).filter_by(user_id=user.id).first()

        response = client.post(
            f'/api/images/transaction/{test_image.id}/basic',
            params={'type': 'black_white'},
            headers={'Authorization': f'''Bearer {user_token['access_token']}'''}
        )
        data = response.json()
        assert response.status_code == 200, response.text
        assert type(data) == dict
        assert data['description'] == 'Test image basic'


def test_update_image(client, session, user, user_token, image, monkeypatch, mock_ratelimiter):
    with patch.object(auth_service.token_manager, 'r') as redis_mock:
        redis_mock.get.return_value = None
        user = session.query(User).filter_by(email=user.get('email')).first()
        test_image = session.query(Image).filter_by(user_id=user.id).first()

        response = client.patch(
            f'/api/images/{test_image.id}',
            json={'description': 'update description', 'tags': 'update_tag'},
            headers={'Authorization': f'''Bearer {user_token['access_token']}'''}
        )
        data = response.json()
        assert response.status_code == 200, response.text
        assert type(data) == dict
        assert data['description'] == 'update description'
        assert data['tags'][0]['name'] == 'update_tag'
        assert 'id' in data


def test_remove_image(client, session, user, user_token, image, monkeypatch, mock_ratelimiter):
    with patch.object(auth_service.token_manager, 'r') as redis_mock:
        redis_mock.get.return_value = None

        user = session.query(User).filter_by(email=user.get('email')).first()
        test_image = session.query(Image).filter_by(user_id=user.id).first()

        response = client.delete(
            f'/api/images/{test_image.id}',
            headers={'Authorization': f'''Bearer {user_token['access_token']}'''}
        )
        data = response.json()
        assert response.status_code == 200, response.text
        assert data['message'] == messages.IMAGE_DELETED
        assert session.query(Image).filter_by(id=test_image.id).first() is None

