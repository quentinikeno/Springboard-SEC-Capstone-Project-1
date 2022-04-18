from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, IntegerRangeField, EmailField
from wtforms.validators import DataRequired, Email, Length, NumberRange

class CreateWorksheetForm(FlaskForm):
    """Form for creating a new Worksheet."""
    name = StringField('Worksheet Name', validators=[DataRequired("Please enter a name for your worksheet.")])
    operations = SelectField('Type of Operations', choices=[
        ('random', 'Random'),
        ('add', 'Addition'), 
        ('sub', 'Subtraction'), 
        ('mul', 'Multiplication'), 
        ('div', 'Division'), 
        ])
    number_questions = IntegerRangeField('Number of Questions', validators=[NumberRange(min=5, max=30)])
    
class UserRegisterEditForm(FlaskForm):
    """Form for signing up and registering users."""
    username = StringField('Username', validators=[DataRequired("Please enter a username for your account.")])
    password = PasswordField('Password', validators=[DataRequired("Please enter a password for your account."), Length(min=6)])
    email = EmailField('Email', validators=[DataRequired("Please enter an email address for your account."), Email()])
    
class UserLoginForm(FlaskForm):
    """Form for logging in users."""
    username = StringField('Username', validators=[DataRequired("Please enter your username to log in.")])
    password = PasswordField('Password', validators=[DataRequired("Please enter your password to log in.")])
    
class UserDeleteForm(FlaskForm):
    """Form for deleting users."""
    password = PasswordField('Password', validators=[DataRequired("Please enter your password to log in.")])
    confirm = SelectField('Are you sure you want to permanently delete your account?', choices=[
        ('no', 'No'),
        ('yes', 'Yes')
        ])