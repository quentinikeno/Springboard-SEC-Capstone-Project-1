import os
from unittest import TestCase

from models import db, User

from sqlalchemy.exc import IntegrityError, InvalidRequestError

os.environ['DATABASE_URL'] = "postgresql:///worksheet_generator_test"

from app import app

db.create_all()

class UserModelTestCase(TestCase):
    """Test User Model."""

    def setUp(self):
        """Create test client, add sample data."""
        
        User.query.delete()
        
        user = User.registerNewUser(
            "JaneDoe",
            "GreatPassword123",
            "test@email.com"
        )
        
        db.session.commit()
        
        self.user = user
        
    def tearDown(self):
        """Rollback any failed transactions."""
        db.session.rollback()

    def test_user_model(self):
        """Does the user model work?"""

        newUser = User(
            email="test@test.com",
            username="testuser",
            password="test"
        )

        db.session.add(newUser)
        db.session.commit()

        self.assertEqual(f"{newUser}", "<User username=testuser>")