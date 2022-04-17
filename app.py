import os

from flask import Flask, render_template, redirect, session, url_for
from flask_debugtoolbar import DebugToolbarExtension
from flask_weasyprint import HTML, render_pdf

from forms import CreateWorksheetForm

import asyncio
from api_helpers import get_math_data

app = Flask(__name__)

app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "very secret key")
toolbar = DebugToolbarExtension(app)

X_MATH_API_BASE_URL = "https://x-math.herokuapp.com/api"

@app.route('/', methods=['GET', 'POST'])
def index():
    """Show form to allow users to specify parameters for their worksheet.  Use the form data to call X-Math API to get math problems."""
    form = CreateWorksheetForm()
    
    if form.validate_on_submit():
        name = form.name.data
        operations = form.operations.data
        number_questions = int(form.number_questions.data)
        
        questions = asyncio.run(get_math_data(X_MATH_API_BASE_URL, operations, number_questions))
        
        # Add questions to session
        session['questions'] = questions
        
        return redirect(url_for('new_worksheet_detail'))
    
    return render_template('index.html', form=form)
 
@app.route('/worksheet/new')
def new_worksheet_detail():
     """Show options for new worksheet, such as downloading and saving."""
     return render_template('new-detail.html')
     
@app.route('/<sheet>/new/pdf')
def render_new_pdf(sheet):
    """Render pdf for new worksheet or answer key."""
    html = render_template(f'{sheet}.html', questions=session['questions'])
    return render_pdf(HTML(string=html))