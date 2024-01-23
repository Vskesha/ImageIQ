from unittest.mock import patch, AsyncMock
from src.services.auth import auth_service
from src.conf import messages

from src.database.models import User, Comment


def test_add_comment(client, session, user_token, user, comment, mock_ratelimiter, monkeypatch):
    with patch.object(auth_service.token_manager, 'r') as r_mock:
        r_mock.get.return_value = None
        mock_image = AsyncMock()
        monkeypatch.setattr('src.repository.images.get_image', mock_image)
        response = client.post(
            f'''/api/comment/{comment['image_id']}''',
            json={'comment': 'Test comment'},
            headers={'Authorization': f'''Bearer {user_token['access_token']}'''}
        )
        data = response.json()
        assert response.status_code == 200, response.text
        assert data['comment'] == comment['comment']


def test_get_comments_by_image_id(client, session, user_token, user, comment, mock_ratelimiter, monkeypatch):
    with patch.object(auth_service.token_manager, 'r') as r_mock:
        r_mock.get.return_value = None
        mock_image = AsyncMock()
        monkeypatch.setattr('src.repository.images.get_image', mock_image)

        response = client.get(
            f'''/api/comment/{comment['image_id']}''',
            headers={'Authorization': f'''Bearer {user_token['access_token']}'''}
        )
        data = response.json()
        assert response.status_code == 200, response.text
        assert data['comment'] == comment['comment']


def test_update_comment(client, session, user_token, user, comment, mock_ratelimiter, monkeypatch):
    with patch.object(auth_service.token_manager, 'r') as r_mock:
        r_mock.get.return_value = None
        user = session.query(User).filter_by(email=user.get('email')).first()
        test_comment = session.query(Comment).filter_by(user_id=user.id).first()
        response = client.patch(
            '/api/comment/1',
            json={'comment': 'New comment'},
            headers={'Authorization': f'''Bearer {user_token['access_token']}'''}
        )
        data = response.json()
        assert response.status_code == 200, response.text
        assert type(data) == dict
        assert data['comment'] == 'New comment'
        assert test_comment.comment == 'New comment'


def test_remove_comment_by_user(client, session, user_token, user, comment, mock_ratelimiter, monkeypatch):
    with patch.object(auth_service.token_manager, 'r') as r_mock:
        r_mock.get.return_value = None
        user = session.query(User).filter_by(email=user.get('email')).first()
        test_comment = session.query(Comment).filter_by(user_id=user.id).first()
        response = client.delete(
            f'/api/comment/{test_comment.id}',
            headers={'Authorization': f'''Bearer {user_token['access_token']}'''}
        )
        data = response.json()
        assert response.status_code == 200, response.text
        assert data['message'] == messages.COMMENT_DELETED


def test_remove_comment_by_admin(client, session, admin_token, admin, mock_ratelimiter, monkeypatch):
    with patch.object(auth_service.token_manager, 'r') as r_mock:
        r_mock.get.return_value = None
        admin = session.query(User).filter_by(email=admin.get('email')).first()
        test_comment = Comment(user_id=admin.id, comment='Test comment')
        session.add(test_comment)
        session.commit()
        response = client.delete(
            f'/api/comment/{test_comment.id}',
            headers={'Authorization': f'''Bearer {admin_token['access_token']}'''}
        )
        data = response.json()
        assert response.status_code == 403, response.text
        assert data["detail"] == messages.MSC403_FORBIDDEN


def test_update_comment_not_found(client, session, user_token, user, comment, mock_ratelimiter, monkeypatch):
    with patch.object(auth_service.token_manager, 'r') as r_mock:
        r_mock.get.return_value = None
        response = client.patch(
            '/api/comment/999',
            json={'comment': 'New comment'},
            headers={'Authorization': f'''Bearer {user_token['access_token']}'''}
        )
        assert response.status_code == 404, response.text


def test_remove_comment_not_found(client, session, admin_token, user, comment, mock_ratelimiter, monkeypatch):
    with patch.object(auth_service.token_manager, 'r') as r_mock:
        r_mock.get.return_value = None
        response = client.delete(
            '/api/comment/9999',
            headers={'Authorization': f'''Bearer {admin_token['access_token']}'''}
        )
        assert response.status_code == 403, response.text
        data = response.json()
        assert data["detail"] == messages.MSC403_FORBIDDEN