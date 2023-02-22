import uuid
from repository.database import db
from models.session import GroupSession

# グループの現在のセッションを取得する関数
def read_group_session_id(group_id):
    session_id = (
        db.session.query(GroupSession.group_session_id)
        .filter(GroupSession.group_id == group_id)
        .first()
    )
    session_id = session_id[0]  # 要素数1のtupleから中身を取り出す

    return session_id

# グループセッションを登録する関数
def register_group_session(group_id):
    group_session_id = str(uuid.uuid1())

    existing_group = read_group(group_id)

    if existing_group != None:  # 存在する場合
        existing_group.group_session_id = group_session_id
    else:  # 存在しない場合
        db.session.add(GroupSession(group_id=group_id, group_session_id=group_session_id))
    
    db.session.commit()

    return group_session_id

def read_group(group_id):
    group =  db.session.query(GroupSession).filter(GroupSession.group_id == group_id).first()

    return group

