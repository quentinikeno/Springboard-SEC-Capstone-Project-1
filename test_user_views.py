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
                
    def test_login_post_wrong_password(self):
        """Can a user login using the wrong password?"""
        with app.test_client() as client:
            data = {'username': 'JaneDoe', 'password': 'wrongPW'}
            resp = client.post('/login', data=data, follow_redirects=True)
            html = resp.get_data(as_text=True)
            
            self.assertEqual(resp.status_code, 200)
            self.assertIn('Invalid username or password.  Please try again.', html)
            with client.session_transaction() as session:
                self.assertIsNone(session.get('user'))
                
    def test_login_post_wrong_username(self):
        """Can a user login using the wrong username?"""
        with app.test_client() as client:
            data = {'username': 'WrongUser', 'password': 'GreatPassword123'}
            resp = client.post('/login', data=data, follow_redirects=True)
            html = resp.get_data(as_text=True)
            
            self.assertEqual(resp.status_code, 200)
            self.assertIn('Invalid username or password.  Please try again.', html)
            with client.session_transaction() as session:
                self.assertIsNone(session.get('user'))
                
    def test_logout(self):
        """Can a user login and then logout?"""
        with app.test_client() as client:
            data = {'username': 'JaneDoe', 'password': 'GreatPassword123'}
            client.post('/login', data=data, follow_redirects=True)
            resp = client.post('/logout', follow_redirects=True)
            html = resp.get_data(as_text=True)
            
            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h1>Math Worksheet Generator</h1>', html)
            self.assertIn("You&#39;ve been logged out successfully.", html)
            with client.session_transaction() as session:
                self.assertIsNone(session.get('user'))
                
    def test_logout_not_logged_in(self):
        """Can a user logout without logging in first?"""
        with app.test_client() as client:
            resp = client.post('/logout', follow_redirects=True)
            html = resp.get_data(as_text=True)
            
            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h1>Log In to Your Account</h1>', html)
            self.assertIn("Access unauthorized.  Please log in first to view this page.", html)
            with client.session_transaction() as session:
                self.assertIsNone(session.get('user'))
                
    def test_user_show(self):
        """Can a user login and then see their user profile show page?"""
        with app.test_client() as client:
            data = {'username': 'JaneDoe', 'password': 'GreatPassword123'}
            client.post('/login', data=data, follow_redirects=True)
            resp = client.get('/user', follow_redirects=True)
            html = resp.get_data(as_text=True)
            
            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h1>Your Profile</h1>', html)
            self.assertIn("JaneDoe", html)
            
    def test_user_show_not_logged_in(self):
        """Can a user see their user profile show page when not logged in?"""
        with app.test_client() as client:
            resp = client.get('/user', follow_redirects=True)
            html = resp.get_data(as_text=True)
            
            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h1>Log In to Your Account</h1>', html)
            self.assertIn("Access unauthorized.  Please log in first to view this page.", html)