from unittest import TestCase

from app import app
#from flask import session
#from models import db

#app.config['SQLALCHEMY_DATABASE_URI'] = 
#app.config['SQLALCHEMY_ECHO'] = False
app.config['TESTING'] = True
app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']
app.config['WTF_CSRF_ENABLED'] = False

#db.drop_all()
#db.create_all()

class WorksheetViewsTestCase(TestCase):
    """Test views for worksheets."""
        
    def test_route_route(self):
        """Testing the route route."""
        with app.test_client() as client:
            resp = client.get("/")
            html = resp.get_data(as_text=True)
            
            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h1>Math Worksheet Generator</h1>', html)
            