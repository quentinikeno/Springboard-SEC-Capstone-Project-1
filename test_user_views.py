from app import app
from unittest import TestCase
from models import db, User
from sqlalchemy.exc import IntegrityError

app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql:///worksheet_generator_test"
app.config['SQLALCHEMY_ECHO'] = False
app.config['TESTING'] = True
app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']
app.config['WTF_CSRF_ENABLED'] = False

db.drop_all()
db.create_all()

class UserViewsTestCase(TestCase):
    """Test User Views."""

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
        
    def test_register_get(self):
        """Can a user see the page to register?"""
        with app.test_client() as client:
            resp = client.get('/register')
            html = resp.get_data(as_text=True)
            
            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h1>Register Your New Account</h1>', html)
            
    def test_register_post(self):
        """Can a user register a new account?"""
        with app.test_client() as client:
            data = {'username': 'test', 'password': 'testPassword', 'email': 'test2@email.com'}
            resp = client.post('/register', data=data, follow_redirects=True)
            html = resp.get_data(as_text=True)
            
            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h1>Your Profile</h1>', html)
            with client.session_transaction() as session:
                self.assertIsNotNone(session['user'])
                
    def test_login_get(self):
        """Can user see the page to login?"""
        with app.test_client() as client:
            resp = client.get('/login')
            html = resp.get_data(as_text=True)
            
            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h1>Log In to Your Account</h1>', html)
            
    def test_login_post(self):
        """Can a user login?"""
        with app.test_client() as client:
            data = {'username': 'JaneDoe', 'password': 'GreatPassword123'}
            resp = client.post('/login', data=data, follow_redirects=True)
            html = resp.get_data(as_text=True)
            
            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h1>Your Profile</h1>', html)
            with client.session_transaction() as session:
                self.assertEqual(session['user'], self.user.id)