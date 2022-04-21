from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from uuid import uuid4
from datetime import datetime

db = SQLAlchemy()

bcrypt = Bcrypt()

def connect_db(app):
    """Connect to database."""

    db.app = app
    db.init_app(app)

class User(db.Model):
    """User model."""
    
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    username = db.Column(db.String(25), unique=True, nullable=False)
    
    password = db.Column(db.Text, nullable=False)
    
    email = db.Column(db.String(50), nullable=False, unique=True)
    
    pdfs = db.relationship('PDF')
    
    def __repr__(self):
        """Representation of User."""
        return f"<User username={self.username}>"
    
    @classmethod
    def register(cls, username, password, email):
        """Hash password and create new user."""
        hashed = bcrypt.generate_password_hash(password)
        # turn bytestring into normal (unicode utf8) string
        hashed_utf8 = hashed.decode("utf8")
        return cls(username=username, password=hashed_utf8, email=email)
    
    @classmethod
    def authenticate(cls, username, password):
        """Check that a user is exists and the password provided is correct."""
        user = User.query.filter_by(username=username).first()
        
        if user and bcrypt.check_password_hash(user.password, password):
            return user
        else:
            return False
        
    @classmethod
    def is_username_taken(cls, username):
        """Check if a username is taken.  Returns a user with a given username if one exists, else returns None."""
        return User.query.filter_by(username=username).first()

    @classmethod
    def is_email_taken(cls, email):
        """Check if a email is taken.  Returns a user with a given email if one exists, else returns None."""
        return User.query.filter_by(email=email).first()
    
class PDF(db.Model):
    """Worksheet and Answer Key File Model."""
    
    __tablename__ = 'pdfs'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    
    unique_s3_filename = db.Column(db.String, unique=True, nullable=False)
    
    filename = db.Column(db.String, nullable=False)
    
    sheet_type = db.Column(db.String, nullable=False)
    
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())
    
    def __repr__(self):
        """Representation of PDF file."""
        return f"<PDF id={self.id} user_id={self.user_id} unique_s3_filename={self.unique_s3_filename} filename={self.filename}>"
    
    @classmethod
    def create_new_pdf(cls, user_id, filename, sheet_type):
        """Create a new instance of PDF model."""
        # Create a unique filename for S3 bucket using uuid.
        unique_s3_filename = f'{uuid4().hex}.pdf'
        return cls(user_id=user_id, unique_s3_filename=unique_s3_filename, filename=filename, sheet_type=sheet_type)