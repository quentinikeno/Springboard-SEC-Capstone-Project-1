from models import db, User
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