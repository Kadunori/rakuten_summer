from repository.database import db

class Group(db.Model):
    __tablename__ = "group"
    id = db.Column(db.Integer, primary_key = True,  autoincrement=True)
    member_id = db.Column(db.String(100))
    member_name = db.Column(db.String(255))
    group_id = db.Column(db.String(255))