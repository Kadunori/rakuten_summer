from models.payment import Payment
from config import db

def connect_payment():
    pass

def insert_payment(payment: Payment):
    db.session.add(payment)
    db.session.commit()