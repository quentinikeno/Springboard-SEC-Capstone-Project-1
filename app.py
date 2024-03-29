import os

from flask import Flask, render_template, redirect, session, request, Response, url_for, flash, g
from flask_debugtoolbar import DebugToolbarExtension
from flask_weasyprint import HTML, render_pdf
from sqlalchemy.exc import IntegrityError
from flask_wtf.csrf import CSRFProtect

from functools import wraps
import asyncio

from models import connect_db, db, User, PDF
from forms import CreateWorksheetForm, UserRegisterEditForm, UserLoginForm, UserDeleteForm
from api_helpers import get_math_data
from resources import get_bucket
from filters import date_time_format


app = Flask(__name__)

app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "very secret key")

uri = os.getenv("DATABASE_URL", 'postgresql:///worksheet_generator')  # or other relevant config var
if uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = uri
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True

toolbar = DebugToolbarExtension(app)

connect_db(app)

csrf = CSRFProtect(app)

app.jinja_env.filters['date_time_format'] = date_time_format

API_BASE_URL = "https://web-production-a407.up.railway.app"

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
    
    if request.method == 'GET':
        form.minimum.data = 0
        form.maximum.data = 100
    
    if form.validate_on_submit():
        name = form.name.data
        operations = form.operations.data
        number_questions = int(form.number_questions.data)
        minimum = form.minimum.data
        maximum = form.maximum.data
        allow_negative = form.allow_negative.data
        
        # params for API get request
        params = dict()
        params["max"] = maximum
        params["min"] = minimum
        if allow_negative:
            params["negative"] = 1
        
        # Do API calls with asyncio
        questions = asyncio.run(get_math_data(API_BASE_URL, operations, number_questions, params))
        
        # Add questions and worksheet name to session
        session['questions'] = questions
        session['name'] = name
        
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
    if g.user:
        return redirect(url_for('user_show'))
    
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
        
        if 'wants_url' in session:
            return redirect(session['wants_url'])
        else:            
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
    return render_template('users/show.html', user=g.user, files=g.user.pdfs)
    
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
                
                flash("Account successfully updated.", "success")
                return redirect(url_for("user_show"))
                
            except IntegrityError:
                db.session.rollback()
                # Check if email and username are already taken
                if User.is_email_taken(email):
                    flash("That email is already taken by another user.  Please use a different email address.", 'danger')
                if User.is_username_taken(username):
                    flash("That username is already taken by another user.  Please use a different username.", 'danger')
                
                return render_template('/users/edit.html', form=form, user=g.user)
            
        flash("Invalid password.  Please make sure your password is correct.", 'danger')
    
    return render_template('users/edit.html', form=form, user=g.user)

@app.route('/user/delete', methods=['GET', 'POST'])
@check_if_authorized
def user_delete():
    """Delete profile for current user."""
    form = UserDeleteForm()
    
    if form.validate_on_submit():
        password = form.password.data
        confirm = form.confirm.data
        
        if confirm == 'no':
            flash('Your account has not been deleted.  To delete your account please select "Yes" from the dropdown below.', "warning")                
            return render_template('/users/delete.html', form=form, user=g.user)
        
        #Authenticate the user to give them permission to edit.
        user = User.authenticate(g.user.username, password)
        
        if user:            
            try:
                do_logout()
                db.session.delete(g.user)
                db.session.commit()
                
                flash("Account successfully deleted.", "success")
                return redirect(url_for("index"))
                
            except IntegrityError:
                db.session.rollback()
                flash("Something went wrong.  Could not delete your account.", "danger")                
                return render_template('/users/delete.html', form=form, user=g.user)
            
        flash("Invalid password.  Please make sure your password is correct.", 'danger')
    
    return render_template('users/delete.html', form=form, user=g.user)

###################################################################################################
# Worksheet S3 Cloud Storage Routes
###################################################################################################
@app.route('/upload', methods=['GET', 'POST'])
@check_session_questions
@check_if_authorized
def upload():
    """Upload worksheet and answer key to S3 bucket."""
    
    if request.method == 'GET':
        return redirect(url_for('new_worksheet_detail'))
    
    user = User.query.get(session['user'])
    
    worksheet_html = render_template('worksheet.html', questions=session['questions'], render=True)
    answer_key_html = render_template('answer-key.html', questions=session['questions'], render=True)
    
    new_worksheet = PDF.create_new_pdf(user_id=user.id, filename=f'{session.get("name")} - Worksheet.pdf', sheet_type='worksheet')
    new_answer_key = PDF.create_new_pdf(user_id=user.id, filename=f'{session.get("name")} - Answer Key.pdf', sheet_type='answer key')
    
    worksheet_filename = new_worksheet.unique_s3_filename
    answer_key_filename = new_answer_key.unique_s3_filename
    worksheet_path = f'pdfs-for-upload/{worksheet_filename}'
    answer_key_path = f'pdfs-for-upload/{answer_key_filename}'
    
    HTML(string=worksheet_html).write_pdf(worksheet_path)
    HTML(string=answer_key_html).write_pdf(answer_key_path)

    # Get bucket object
    my_bucket = get_bucket()
    # Pass in file names and upload to Bucket
    my_bucket.upload_file(worksheet_path, worksheet_filename)
    my_bucket.upload_file(answer_key_path, answer_key_filename)
    # Remove files from file system after upload to S3
    os.remove(worksheet_path)
    os.remove(answer_key_path)
    
    # Save worksheet metadata to db.
    db.session.add_all([new_worksheet, new_answer_key])
    db.session.commit()
    
    flash("Worksheet and answer key successfully saved!", "success")
    return redirect(url_for('user_show'))

@app.route('/delete', methods=['POST'])
@check_if_authorized
def delete():
    """Delete pdf file from S3 bucket."""
    # Get the file key from hidden field in delete form.
    key = request.form['key']

    my_bucket = get_bucket()
    # Delete the appropriate file using the key.
    my_bucket.Object(key).delete()
    
    # Delete worksheet metadata from db.
    pdf = PDF.query.filter( (PDF.user_id == g.user.id) & (PDF.unique_s3_filename == key)).first()
    db.session.delete(pdf)
    db.session.commit()
    
    flash('File deleted successfully.', 'success')
    return redirect(url_for('user_show'))

@app.route('/download', methods=['POST'])
@check_if_authorized
def download():
    """Download pdf file from S3 bucket."""
    # Get the file key and filename from hidden field in delete form.
    key = request.form['key']
    filename = request.form['filename']
    
    my_bucket = get_bucket()
    # Get file object
    file_obj = my_bucket.Object(key).get()
    
    return Response(
        file_obj['Body'].read(), 
        mimetype='application/pdf', 
        headers={"Content-Disposition": f'attachment; filename="{format(filename)}"'}
        )
    
###################################################################################################
# 404 Route
###################################################################################################
@app.errorhandler(404)
def not_found(e):
    """Render to 404 error page."""
    return render_template('404.html',)