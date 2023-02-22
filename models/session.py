from repository.database import db

# グループの今のセッションが何かを保存するテーブル
class GroupSession(db.Model):
    __tablename__ = 'group_session'
    group_id = db.Column(db.String(100), primary_key=True)
    group_session_id = db.Column(db.String(100))