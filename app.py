import os

from flask import Flask, render_template, redirect, session, request, url_for, flash, g
from flask_debugtoolbar import DebugToolbarExtension
from flask_weasyprint import HTML, render_pdf

from sqlalchemy.exc import IntegrityError

from models import connect_db, db, User

from functools import wraps

from forms import CreateWorksheetForm, UserRegisterEditForm, UserLoginForm

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

###################################################################################################
# Route Decorators
###################################################################################################

def check_session_questions(function):
    """Check if there are questions in session.  If not redirect to index route."""
    @wraps(function)
    def check_session_questions_decorator(*args, **kwargs):
        if session.get('questions'):
            return function(*args, **kwargs)
        else:
            flash('Please generate a new worksheet before accessing that page.', 'warning')
            return redirect(url_for('index'))
    return check_session_questions_decorator

def check_if_authorized(function):
    """Check if user is logged in using flask global variable.  If not redirect to login route."""
    @wraps(function)
    def check_if_authorized_decorator(*args, **kwargs):
        if not g.user:
            flash("Access unauthorized.  Please log in first to view this page.", "danger")
            # Set in the session the url that the user was trying to go to before logging in, so we can redirect later.
            session["wants_url"] = request.url
            return redirect(url_for("login"))
        else:
            return function(*args, **kwargs)
    return check_if_authorized_decorator

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
        
        # Do API calls with asyncio
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
    if 'wants_url' in session:
        del session['wants_url']

###################################################################################################
# User Register/Log In/Log Out Routes
###################################################################################################

@app.route('/register', methods=['GET', 'POST'])
def user_register():
    """Show form to register new user."""
    form = UserRegisterEditForm()
    
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        
        try:            
            new_user = User.register(username, password, email)
            db.session.add(new_user)
            db.session.commit()
        
        except IntegrityError:
            db.session.rollback()
            # Check if email and username are already taken
            if User.is_email_taken(email):
                flash("That email is already taken by another user.  Please use a different email address.", 'danger')           
            if User.is_username_taken(username):
                flash("That username is already taken by another user.  Please use a different username.", 'danger')
            
            return render_template('/users/register.html', form=form)
            
        do_login(new_user)
            
        return redirect(url_for('user_show'))
        
    return render_template('/users/register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Authenticate a user."""
    if g.user:
        return redirect(url_for('user_show'))
    
    form = UserLoginForm()
    
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        
        user = User.authenticate(username, password)
        
        if user:
            do_login(user)
            flash(f'Login succesful!  Welcome back {user.username}!', 'success')
            if 'wants_url' in session:
                return redirect(session['wants_url'])
            else:
                return redirect(url_for('user_show'))
        else:
            flash('Invalid username or password.  Please try again.', 'danger')
        
    return render_template('/users/login.html', form=form)

@app.route('/logout', methods=['POST'])
@check_if_authorized
def logout():
    """Log out a user."""
    do_logout()
    flash("You've been logged out successfully.", "success")
    return redirect(url_for('index'))

###################################################################################################
# User Routes
###################################################################################################

@app.route('/user')
@check_if_authorized
def user_show():
    """Show details for user."""
    return render_template('users/show.html', user=g.user)
    
@app.route('/user/edit', methods=['GET', 'POST'])
@check_if_authorized
def user_edit():
    """Edit profile for current user."""
    form = UserRegisterEditForm()
    
    if request.method == 'GET':
        form.username.data = g.user.username
        form.email.data = g.user.email
    
    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = form.password.data
        
        #Authenticate the user to give them permission to edit.
        user = User.authenticate(g.user.username, password)
        
        if user:            
            try:
                user.username = username
                user.email = email
                
                db.session.add(user)
                db.session.commit()
                
                flash("Profile successfully updated.", "success")
                return redirect(url_for("user_show"))
                
            except IntegrityError:
                db.session.rollback()
                # Check if email and username are already taken
                if User.is_email_taken(email):
                    flash("That email is already taken by another user.  Please use a different email address.", 'danger')
                if User.is_username_taken(username):
                    flash("That username is already taken by another user.  Please use a different username.", 'danger')
                
                return render_template('/users/edit.html', form=form, user=g.user)
            
        flash("Invalid username or password.", 'danger')
    
    return render_template('users/edit.html', form=form, user=g.user)