from xml.sax.handler import DTDHandler
from repository.database import db
from models.payment import Payment

# 支払い情報のキャンセルを行う関数
def cancel_payment(del_group_id,del_group_session_id,del_pay_session_id):
    target_list = db.session.query(Payment).filter_by(group_id=del_group_id,
                                                group_session_id=del_group_session_id,
                                                pay_session_id=del_pay_session_id).all()
    for target in target_list:
        db.session.delete(target)
        db.session.commit()