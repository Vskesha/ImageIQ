from unittest.mock import patch
from src.services.auth import auth_service
from src.conf import messages
from src.database.models import User
from src.database.models import Image, TransformationsType, Rating
from datetime import datetime



def test_add_rating(client, session, user_token, mock_ratelimiter):
    with patch.object(auth_service.token_manager, 'r') as r_mock:
        r_mock.get.return_value = None
        user2 = User(
            id=3,
            username='Test',
            email='tttest@test',
            password='Qw1231231ty@1',
            role='user',
            status_active=True,
            confirmed=True)

        session.add(user2)
        session.commit()
        test_image = Image(
            id=4,
            description='Test image',
            type=TransformationsType.basic,
            link='test_link',
            user_id=user2.id,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        session.add(test_image)
        session.commit()
        response = client.post(
            f'/api/ratings/{test_image.id}',
            json={"rating": 5.0},
            headers={'Authorization': f'Bearer {user_token["access_token"]}'}
        )
        assert response.status_code == 200
        assert "rating" in response.json()


def test_add_rating_self_image(client, session, user, user_token, mock_ratelimiter):
    with patch.object(auth_service.token_manager, 'r') as r_mock:
        r_mock.get.return_value = None
        test_image = Image(
            id=5,
            description='Test image2',
            type=TransformationsType.basic,
            link='test_link_t',
            user_id=user.get('id'),
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        session.add(test_image)
        session.commit()
        response = client.post(
            f'/api/ratings/{test_image.id}',
            json={"rating": 5.0},
            headers={'Authorization': f'Bearer {user_token["access_token"]}'}
        )
        assert response.status_code == 400, response.text
        data = response.json()
        print('AAdata', data)
        assert data['detail'] == messages.CANNOT_RATE_OWN_IMAGE


def test_remove_rating(client, session, user, user_token, mock_ratelimiter):
    with patch.object(auth_service.token_manager, 'r') as r_mock:
        r_mock.get.return_value = None
        test_user = User(
            username="test_user",
            email="test@example.com",
            password="testpassword",
            role="admin",
        )
        session.add(test_user)
        session.commit()
        test_rating = Rating(user_id=test_user.id, rating=5.0)
        session.add(test_rating)
        session.commit()
        response = client.delete(
            f"/api/ratings/{test_rating.id}",
            headers={'Authorization': f'Bearer {user_token["access_token"]}'}
        )
        assert response.status_code == 200
        assert response.json() == {'message': 'Rating removed'}



def test_get_all_ratings(client, session, user, user_token, mock_ratelimiter):
    with patch.object(auth_service.token_manager, 'r') as r_mock:
        r_mock.get.return_value = None
        test_image = Image(description="Test image", user_id=user.get('id'), link="test_image_link_test")
        session.add(test_image)
        session.commit()

        test_ratings = Rating(user_id=user.get('id'), image_id=test_image.id, rating=4.5),
        session.add_all(test_ratings)
        session.commit()

        response = client.get(
            f"/api/ratings/{test_image.id}/all",
            headers={"Authorization": f"Bearer {user_token['access_token']}"},
        )

        assert response.status_code == 200
        print("Test image", response.json())
        expected_ratings = [{'rating': 4.5, 'id': 2, 'user_id': user.get('id'),'image_id': test_image.id, 'created_at': test_image.created_at.strftime('%Y-%m-%dT%H:%M:%S'),}]
        assert response.json() == expected_ratings


def test_get_all_ratings_not_found(client, session, user, user_token, mock_ratelimiter):
    with patch.object(auth_service.token_manager, 'r') as r_mock:
        r_mock.get.return_value = None
        response = client.get(
            f"/api/ratings/999/all",
            headers={"Authorization": f"Bearer {user_token['access_token']}"},
        )

        assert response.status_code == 404
        assert response.json() == {'detail': 'Image Not Found'}
