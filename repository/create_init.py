from models.group import Group
from models.payment import Payment
from models.session import GroupSession
from repository.database import db

def create_init(app):
    with app.app_context():
        db.drop_all()
        db.create_all()
        # user_create()
        # db.session.commit()
    
# def user_create():
    # テストデータ追加