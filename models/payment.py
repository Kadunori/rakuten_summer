from repository.database import db
from datetime import datetime

class Payment(db.Model):
    __tablename__ = 'payment'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    group_id = db.Column(db.String(100))
    group_session_id = db.Column(db.String(100))
    pay_session_id = db.Column(db.String(100))
    pay_user_id = db.Column(db.String(100))
    pay_user_name = db.Column(db.String(100))
    debtor_id = db.Column(db.String(100))
    debtor_name = db.Column(db.String(100))
    amount = db.Column(db.Float, default=0)
    purpose = db.Column(db.String(255))
    time = db.Column(db.DateTime, nullable=False, default=datetime.now)