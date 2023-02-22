from tokenize import group
from unicodedata import name
from models.payment import Payment
from models.group import Group
from repository.database import db
import uuid
import datetime



#group tableから同じグループに所属するメンバーの情報(id, 名前)を辞書として取得
def get_group_member_info(current_group_id):
    id_list = db.session.query(Group.member_id, Group.member_name).filter(Group.group_id == current_group_id).all()#member_idカラムを指定して列をリスト取得 !!whereを使ってtableIDを指定
    # ist = db.session.query(Group.member_name).filter(Group.group_id == current_group_id).all()#member_nameカラムを指定して列をリスト取得
    info_dic = dict(id_list) #info_dic(メンバーのidと名前を紐付けする)にidとnameを追加
    return info_dic #{id:name}の形で返す

#名前からIDを取得する
def match_id_name(dic,serch_name):
    for dic_id, dic_name in dic.items():
        if serch_name == dic_name:
            return dic_id

#現在時刻の取得(str型)
def get_time():
    t_delta = datetime.timedelta(hours=9)
    JST = datetime.timezone(t_delta, 'JST')
    now = datetime.datetime.now(JST)
    return now

#main関数######################################################
#Payment tableに支払情報を追加する
def register_pay_info(word, pay_user_id, pay_user_name, current_group_id, group_session_id):
    t = get_time()                                   #現在時刻を取得  
    time = t.strftime('%Y/%m/%d %H:%M:%S')           #現在時刻をYYYY/MM/DD HH:MM:SSで取得
    pay_session_id = str(uuid.uuid1())
    group_id = current_group_id
    group_dic = get_group_member_info(current_group_id)              #メンバーのidと名前を紐付けした辞書を取得する
    amounts = int(word[1])                         # 金額
    purpose = word[2]  # 用途
    if len(word) < 4:  # 負担した相手が指定されていないとき
        # debtors = db.session.query(Group.member_name).filter(Group.group_id == current_group_id).all()#グループ全員の情報をgroup_repositoryを通じて取ってくる
        debtors = list(map(lambda x: x[0], db.session.query(Group.member_name).filter(Group.group_id == current_group_id, Group.member_id != pay_user_id).all())) #グループ全員の情報をgroup_repositoryを通じて取ってくる
    else:
        debtors = word[3:] # 負担した相手
    amount = amounts / (len(debtors) + 1)
    for debtor_name in debtors:
        debtor_id = match_id_name(group_dic, debtor_name)#debtorからIDと名前を取得する
        payment = Payment(group_id=group_id, group_session_id=group_session_id, pay_session_id=pay_session_id, pay_user_id=pay_user_id, 
        pay_user_name=pay_user_name, debtor_id=debtor_id, debtor_name=debtor_name, amount=amount, purpose=purpose, time=time
        )# フィールドを埋める
        db.session.add(payment)#paymentテーブルに追加
    db.session.commit()
    
    return pay_session_id