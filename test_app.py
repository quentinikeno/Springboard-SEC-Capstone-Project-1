from unittest import TestCase

from app import app
from flask import session, url_for
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
            
    def test_route_post_route(self):
        """Testing submitting the form to create a new worksheet on the root route."""
        with app.test_client() as client:
            data = {'name': 'Test', 'operations': 'random', 'number_questions': 20}
            resp = client.post('/', data=data, follow_redirects=True)
            html = resp.get_data(as_text=True)
            
            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h1>Generated Worksheet</h1>', html)
            with client.session_transaction() as session:
                self.assertIsNotNone(session["questions"])
                
    def test_worksheet_pdf_route(self):
        """Testing rendering of worksheet pdf."""
        with app.test_client() as client:
            with client.session_transaction() as session:
                # Add questions to session
                session['questions'] = [{'answer': 44, 'expression': '88 / 2', 'first': 88, 'operation': '/', 'second': 2}, 
                                        {'answer': 1440, 'expression': '40 * 36', 'first': 40, 'operation': '*', 'second': 36}, 
                                        {'answer': 30, 'expression': '45 - 15', 'first': 45, 'operation': '-', 'second': 15},
                                        {'answer': 12, 'expression': '40 - 28', 'first': 40, 'operation': '-', 'second': 28}, 
                                        {'answer': 15, 'expression': '56 - 41', 'first': 56, 'operation': '-', 'second': 41}]
            resp = client.get('/worksheet/new/pdf')
            
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(resp.mimetype, 'application/pdf')
            
    def test_worksheet_pdf_route_no_questions_in_session(self):
        """Testing rendering of worksheet pdf."""
        with app.test_client() as client:
            resp = client.get('/worksheet/new/pdf', follow_redirects=True)
            html = resp.get_data(as_text=True)
            
            self.assertEqual(resp.status_code, 200)
            self.assertIn('Please generate a new worksheet before accessing that page.', html)