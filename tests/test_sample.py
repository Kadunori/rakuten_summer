from uuid import uuid1
from repository.database import db
from service.group_service import register_user
from service.how_to_use import show_how_to_use
from service.payment_info import register_pay_info
from service.cancel_payment import cancel_payment
from service.pay_off import pay_off, pay_off_data_to_string
from service.debtor_attribute_service import set_debtor_attribute
from models.group import Group
from models.payment import Payment
import service.group_session_service as group_session_service


# Groupテーブルに登録できるかテスト
def test_register():
    register_user(0, "中野", 0)
    group = db.session.query(Group).first()
    assert group.group_id=="0" and group.member_name=="中野" and group.member_id=="0"

# 全員分の支払い情報登録ができるかテスト
def test_register_pay_info_all():
    group_id = "0"
    member_id_list = ["0", "1", "2", "3"]
    member_name_list = ["太郎", "花子", "雄二", "中野"]
    for member_id, member_name in zip(member_id_list, member_name_list):
        register_user(member_id, member_name,  group_id)
    word = ["割り勘マン", 1000, "昼ごはん"]
    pay_user_id = "3"
    pay_user_name = "中野"
    group_session_id = "0"
    register_pay_info(word, pay_user_id, pay_user_name, group_id, group_session_id)
    payment = db.session.query(Payment).all()
    assert len(member_id_list)-1 == len(payment)

# 指定メンバーの支払い情報が登録できるかテスト
def test_register_pay_info_specified():
    group_id = "0"
    member_id_list = ["0", "1", "2", "3"]
    member_name_list = ["太郎", "花子", "雄二", "中野"]
    for member_id, member_name in zip(member_id_list, member_name_list):
        register_user(member_id, member_name,  group_id)
    word = ["割り勘マン", 1000, "昼ごはん", "太郎", "花子"]
    pay_user_id = "3"
    pay_user_name = "中野"
    group_session_id = "0"
    register_pay_info(word, pay_user_id, pay_user_name, group_id, group_session_id)
    payment = db.session.query(Payment).all()
    assert len(word[3:]) == len(payment)

# 支払い情報のキャンセルができるかテスト
def test_cancel_payment():
    group_id = "0"
    member_id_list = ["0", "1", "2", "3"]
    member_name_list = ["太郎", "花子", "雄二", "中野"]
    for member_id, member_name in zip(member_id_list, member_name_list):
        register_user(member_id, member_name,  group_id)
    word = ["割り勘マン", 1000, "昼ごはん"]
    pay_user_id = "3"
    pay_user_name = "中野"
    group_session_id = "0"
    pay_session_id = register_pay_info(word, pay_user_id, pay_user_name, group_id, group_session_id)
    cancel_payment(group_id, group_session_id, pay_session_id)

# 精算が出来るかテスト(全員)
def test_pay_off():
    group_id = "0"
    member_id_list = ["0", "1", "2", "3"]
    member_name_list = ["太郎", "花子", "雄二", "中野"]
    group_session_id = "0"
    for member_id, member_name in zip(member_id_list, member_name_list):
        register_user(member_id, member_name,  group_id)

    pay_user_id = "0"
    pay_user_name = "太郎"
    word = ["割り勘マン", 1000, "朝ごはん"]
    pay_session_id = register_pay_info(word, pay_user_id, pay_user_name, group_id, group_session_id)
    pay_user_id = "1"
    pay_user_name = "花子"
    word = ["割り勘マン", 2000, "昼ごはん"]
    pay_session_id = register_pay_info(word, pay_user_id, pay_user_name, group_id, group_session_id)
    pay_user_id = "2"
    pay_user_name = "雄二"
    word = ["割り勘マン", 3000, "夜ごはん"]
    pay_session_id = register_pay_info(word, pay_user_id, pay_user_name, group_id, group_session_id)

    result = pay_off(group_id, group_session_id)
    assert [['3', '2', 1500], ['0', '1', 500]] == result

# 精算が出来るかテスト(指定メンバー)
def test_pay_off_specified():
    group_id = "0"
    member_id_list = ["0", "1", "2"]
    member_name_list = ["太郎", "花子", "雄二"]
    group_session_id = "0"
    for member_id, member_name in zip(member_id_list, member_name_list):
        register_user(member_id, member_name,  group_id)

    pay_user_id = "0"
    pay_user_name = "太郎"
    word = ["割り勘マン", 3000, "朝ごはん"]
    pay_session_id = register_pay_info(word, pay_user_id, pay_user_name, group_id, group_session_id)
    pay_user_id = "1"
    pay_user_name = "花子"
    word = ["割り勘マン", 4000, "昼ごはん"]
    pay_session_id = register_pay_info(word, pay_user_id, pay_user_name, group_id, group_session_id)
    pay_user_id = "2"
    pay_user_name = "雄二"
    word = ["割り勘マン", 5000, "夜ごはん"]
    pay_session_id = register_pay_info(word, pay_user_id, pay_user_name, group_id, group_session_id)
    pay_user_id = "0"
    pay_user_name = "太郎"
    word = ["割り勘マン", 9000, "カフェ", "花子"]
    pay_session_id = register_pay_info(word, pay_user_id, pay_user_name, group_id, group_session_id)
    result = pay_off(group_id, group_session_id)
    assert [['1', '0', 3500], ['1', '2', 1000]] == result

# 精算が出来るかテスト(重みづけあり)
def test_pay_off_weighting():
    group_id = "0"
    member_id_list = ["0", "1", "2", "3"]
    member_name_list = ["太郎", "花子", "雄二", "中野"]
    group_session_id = "0"
    for member_id, member_name in zip(member_id_list, member_name_list):
        register_user(member_id, member_name,  group_id)
    
    # 先輩を決定
    from models.debtor_attribute import DebtorAttribute
    set_debtor_attribute(member_id_list[3], group_session_id, "先輩")
    # print(db.session.query(DebtorAttribute).all())

    pay_user_id = "0"
    pay_user_name = "太郎"
    word = ["割り勘マン", 1000, "朝ごはん"]
    pay_session_id = register_pay_info(word, pay_user_id, pay_user_name, group_id, group_session_id)
    pay_user_id = "1"
    pay_user_name = "花子"
    word = ["割り勘マン", 2000, "昼ごはん"]
    pay_session_id = register_pay_info(word, pay_user_id, pay_user_name, group_id, group_session_id)
    pay_user_id = "2"
    pay_user_name = "雄二"
    word = ["割り勘マン", 3000, "夜ごはん"]
    pay_session_id = register_pay_info(word, pay_user_id, pay_user_name, group_id, group_session_id)

    result = pay_off(group_id, group_session_id)
    assert [['3', '2', 1700], ['3', '1', 400], ['0', '1', 300]] == result


# 精算メッセージのテスト
def test_pay_off_message():
    group_id = "0"
    member_id_list = ["0", "1", "2", "3"]
    member_name_list = ["太郎", "花子", "雄二", "中野"]
    group_session_id = "0"
    for member_id, member_name in zip(member_id_list, member_name_list):
        register_user(member_id, member_name,  group_id)

    pay_user_id = "0"
    pay_user_name = "太郎"
    word = ["割り勘マン", 1000, "朝ごはん"]
    pay_session_id = register_pay_info(word, pay_user_id, pay_user_name, group_id, group_session_id)
    pay_user_id = "1"
    pay_user_name = "花子"
    word = ["割り勘マン", 2000, "昼ごはん"]
    pay_session_id = register_pay_info(word, pay_user_id, pay_user_name, group_id, group_session_id)
    pay_user_id = "2"
    pay_user_name = "雄二"
    word = ["割り勘マン", 3000, "夜ごはん"]
    pay_session_id = register_pay_info(word, pay_user_id, pay_user_name, group_id, group_session_id)

    result = pay_off(group_id, group_session_id)
    assert [['3', '2', 1500], ['0', '1', 500]] == result

    result_message = pay_off_data_to_string(result, group_id)

    expect_result_message = "精算結果\n中野が雄二に1500円払う\n太郎が花子に500円払う"

    assert expect_result_message == result_message


# セッションidを登録する関数
def test_read_group_session_id():
    group_id = str(uuid1())
    session_id = group_session_service.register_group_session(group_id)
    db_session_id = group_session_service.read_group_session_id(group_id)

    assert session_id == db_session_id

