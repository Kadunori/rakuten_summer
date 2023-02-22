from repository.database import db
from models.group import Group

# グループにメンバーを登録するための関数
def register_user(reg_user_id, req_user_name, reg_group_id):
    user = Group(
        member_id=reg_user_id, member_name=req_user_name, group_id=reg_group_id
    )

    db.session.add(user)
    db.session.commit()


# Trueなら既にユーザがいる
def exist_user(check_user_id, check_group_id):
    users = list(
        db.session.query(Group)
        .filter(Group.member_id == check_user_id, Group.group_id == check_group_id)
        .all()
    )

    return len(users) != 0
