from models import db, User, PDF
from app import app

db.drop_all()
db.create_all()

user = User.register(
            "test",
            "test",
            "test@email.com"
        )
        
db.session.add(user)
db.session.commit()