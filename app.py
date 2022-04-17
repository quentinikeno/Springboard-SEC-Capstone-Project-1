import os

from flask import Flask, render_template, redirect, session, url_for, flash, g
from flask_debugtoolbar import DebugToolbarExtension
from flask_weasyprint import HTML, render_pdf

from sqlalchemy.exc import IntegrityError

from models import connect_db, db, User

from functools import wraps

from forms import CreateWorksheetForm, UserRegisterForm

import asyncio
from api_helpers import get_math_data

app = Flask(__name__)

app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "very secret key")
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///worksheet_generator'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True

toolbar = DebugToolbarExtension(app)

connect_db(app)

X_MATH_API_BASE_URL = "https://x-math.herokuapp.com/api"

def check_session_questions(f):
    """Check if there are questions in session.  If not redirect to index route."""
    @wraps(f)
    def decorator(*args, **kwargs):
        if session.get('questions'):
            return f(*args, **kwargs)
        else:
            flash('Please generate a new worksheet before accessing that page.', 'warning')
            return redirect(url_for('index'))
    return decorator

###################################################################################################
# Worksheet Routes
###################################################################################################

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
@check_session_questions
def new_worksheet_detail():
     """Show options for new worksheet, such as downloading and saving."""
     return render_template('new-detail.html')
     
@app.route('/<sheet>/new/pdf')
@check_session_questions
def render_new_pdf(sheet):
    """Render pdf for new worksheet or answer key."""
    html = render_template(f'{sheet}.html', questions=session['questions'])
    return render_pdf(HTML(string=html))

###################################################################################################
# User Log In and Log Out
###################################################################################################
@app.before_request
def add_user_to_g():
    """If user is logged in and in session add the user to flask global."""

    if 'user' in session:
        g.user = User.query.get(session['user'])
    else:
        g.user = None


def do_login(user):
    """Add user to session when logging in."""
    session['user'] = user.id


def do_logout():
    """Remove user from session when logging out."""
    if 'user' in session:
        del session['user']

###################################################################################################
# User Routes
###################################################################################################

@app.route('/register', methods=['GET', 'POST'])
def user_register():
    """Show form to register new user."""
    form = UserRegisterForm()
    
    if form.validate_on_submit():
        try:
            username = form.username.data
            password = form.password.data
            email = form.email.data
            
            new_user = User.register(username, password, email)
            db.session.add(new_user)
            db.session.commit()
            
            do_login(new_user)
            
            return redirect(url_for(user_show, username=new_user.username))
        
        except IntegrityError:
            flash("Username already taken", 'danger')
        
    return render_template('/user-templates/user-register.html', form=form)

@app.route('/users/<username>')
def user_show(username):
    """Show details for user."""
    