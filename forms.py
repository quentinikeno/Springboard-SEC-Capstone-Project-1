from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, IntegerRangeField
from wtforms.validators import DataRequired, Email, Length, NumberRange

class CreateWorksheetForm(FlaskForm):
    """Form for creating a new Worksheet."""

    name = StringField('Name', validators=[DataRequired()])
    operations = SelectField('Type of Operations', choices=[
        ('random', 'Random')
        ('add', 'Addition'), 
        ('sub', 'Subtraction'), 
        ('mul', 'Multiplication'), 
        ('div', 'Division'), 
        ])
    number_questions = IntegerRangeField('Number of Questions', validators=[NumberRange(min=5, max=20)])