from app import app
from unittest import TestCase
from models import db, User
from sqlalchemy.exc import IntegrityError, InvalidRequestError

app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql:///worksheet_generator_test"
app.config['TESTING'] = True

db.drop_all()
db.create_all()

class UserModelTestCase(TestCase):
    """Test User Model."""

    def setUp(self):
        """Create test client, add sample data."""
        
        User.query.delete()
        
        user = User.register(
            "JaneDoe",
            "GreatPassword123",
            "test@email.com"
        )
        
        db.session.add(user)
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
        
    def test_user_register(self):
        """Can a new user register?"""
        
        user = User.register("testUser", "SecretPassword123", "test@mail.com")
        db.session.add(user)
        db.session.commit()
        
        self.assertIsInstance(user, User)
    
    def test_user_register_non_unique_username(self):
        """Test if User.register fails to create a new user given non-unique username."""
        user = User.register("JaneDoe", "password", "testurl@mail.com")
        db.session.add(user)
        
        with self.assertRaises(IntegrityError):
            db.session.commit()

            
    def test_user_register_nullable_fields(self):
        """Test if User.register fails to create a new user given non-nullable fields not provided."""
        
        with self.assertRaises(TypeError):
            User.register()