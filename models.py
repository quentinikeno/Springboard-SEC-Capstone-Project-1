from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()

bcrypt = Bcrypt()

def connect_db(app):
    """Connect to database."""

    db.app = app
    db.init_app(app)

class User(db.Model):
    """User model."""
    
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement = True)
    
    username = db.Column(db.String(25), unique=True, nullable=False)
    
    password = db.Column(db.Text, nullable=False)
    
    email = db.Column(db.String(50), nullable=False, unique=True)
    
    def __repr__(self):
        """Representation of User."""
        return f"<User username={self.username}>"
    
    @classmethod
    def registerNewUser(cls, username, password, email):
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