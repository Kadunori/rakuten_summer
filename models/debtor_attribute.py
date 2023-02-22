from repository.database import db

class DebtorAttribute(db.Model):
    __tablename__ = "debtor_attribute"
    id = db.Column(db.Integer, primary_key = True,  autoincrement=True)
    member_id = db.Column(db.String(100))
    group_session_id = db.Column(db.String(100))
    attribute = db.Column(db.String(100))  # 現在はドライバーと先輩