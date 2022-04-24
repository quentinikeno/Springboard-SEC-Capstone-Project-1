from unittest import TestCase

from app import app

app.config['TESTING'] = True
app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']
app.config['WTF_CSRF_ENABLED'] = False

class WorksheetViewsTestCase(TestCase):
    """Test views for worksheets."""
        
    def test_index_route(self):
        """Testing the index route."""
        with app.test_client() as client:
            resp = client.get("/")
            html = resp.get_data(as_text=True)
            
            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h1>Math Worksheet Generator</h1>', html)
            
    def test_index_post_route(self):
        """Testing submitting the form to create a new worksheet on the index route."""
        with app.test_client() as client:
            data = {'name': 'Test', 'operations': 'random', 'number_questions': 20, 'minimum': 0, 'maximum': 10, 'allow_negative': True}
            resp = client.post('/', data=data, follow_redirects=True)
            html = resp.get_data(as_text=True)
            
            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h1 class="text-center">Generated Worksheet</h1>', html)
            with client.session_transaction() as session:
                self.assertIsNotNone(session["questions"])
                
    def test_new_worksheet_route_no_questions_in_session(self):
        """Testing redirect from new worksheet route if questions are not in session."""
        with app.test_client() as client:
            resp = client.get('/worksheet/new', follow_redirects=True)
            html = resp.get_data(as_text=True)
            
            self.assertEqual(resp.status_code, 200)
            self.assertIn('Please generate a new worksheet before accessing that page.', html)
                
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
        """Testing redirect from pdf route if questions are not in session."""
        with app.test_client() as client:
            resp = client.get('/worksheet/new/pdf', follow_redirects=True)
            html = resp.get_data(as_text=True)
            
            self.assertEqual(resp.status_code, 200)
            self.assertIn('Please generate a new worksheet before accessing that page.', html)
            
    def test_answer_key_pdf_route(self):
        """Testing rendering of answer key pdf."""
        with app.test_client() as client:
            with client.session_transaction() as session:
                # Add questions to session
                session['questions'] = [{'answer': 44, 'expression': '88 / 2', 'first': 88, 'operation': '/', 'second': 2}, 
                                        {'answer': 1440, 'expression': '40 * 36', 'first': 40, 'operation': '*', 'second': 36}, 
                                        {'answer': 30, 'expression': '45 - 15', 'first': 45, 'operation': '-', 'second': 15},
                                        {'answer': 12, 'expression': '40 - 28', 'first': 40, 'operation': '-', 'second': 28}, 
                                        {'answer': 15, 'expression': '56 - 41', 'first': 56, 'operation': '-', 'second': 41}]
            resp = client.get('/answer-key/new/pdf')
            
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(resp.mimetype, 'application/pdf')
            
    def test_answer_key_pdf_route_no_questions_in_session(self):
        """Testing redirect from answer key pdf route if questions are not in session."""
        with app.test_client() as client:
            resp = client.get('/answer-key8/new/pdf', follow_redirects=True)
            html = resp.get_data(as_text=True)
            
            self.assertEqual(resp.status_code, 200)
            self.assertIn('Please generate a new worksheet before accessing that page.', html)
            
    def test_404_page(self):
        """Test 404 page."""
        with app.test_client() as client:
            resp = client.get('/badroute404')
            
            self.assertEqual(404, resp.status_code)
            
    def test_404_page(self):
        """Test 404 page redirect."""
        with app.test_client() as client:
            resp = client.get('/badroute404', follow_redirects=True)
            html = resp.get_data(as_text=True)
            
            self.assertEqual(200, resp.status_code)
            self.assertIn('<h1>The page you are looking for does not exist!</h1>', html)