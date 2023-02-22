from repository.database import db
from models.debtor_attribute import DebtorAttribute

def set_debtor_attribute(member_id, group_session_id, attribute):
    debtor_attribute = DebtorAttribute(member_id=member_id, group_session_id=group_session_id, attribute=attribute)
    db.session.add(debtor_attribute)
    db.session.commit()