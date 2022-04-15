import os

from flask import Flask, render_template
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
    form = CreateWorksheetForm()
    
    if form.validate_on_submit():
        name = form.name.data
        operations = form.operations.data
        number_questions = int(form.number_questions.data)
        
        questions = asyncio.run(get_math_data(X_MATH_API_BASE_URL, operations, number_questions))
        
        html = render_template('worksheet.html', questions=questions)
        return render_pdf(HTML(string=html))
    
    return render_template('index.html', form=form)
 