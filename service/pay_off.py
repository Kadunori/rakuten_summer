from copy import deepcopy
from re import A
from repository.database import db
from models.group import Group
from models.payment import Payment
from models.debtor_attribute import DebtorAttribute
from service import payment_info
import math
from decimal import Decimal, ROUND_HALF_UP

def pay_off(group_id, session_id):
  
  member_id = db.session.query(Group.member_id).filter(Group.group_id == group_id).all()
  member_id = list(map(lambda x: x[0], member_id))

  payments= db.session.query(Payment).filter(Payment.group_session_id == session_id).all()
  payer = [] #支払った人
  debtor = [] #支払ってもらった人
  amount = [] #金額

  for payment in payments:
    payer.append(payment.pay_user_id)
    debtor.append(payment.debtor_id)
    amount.append(payment.amount)

  payNum = [] #個々の負担額
  money = 0
  payment_dict = {}
  underpayment = {}
  overpayment = {}
  underpayment_sorted = []
  overpayment_sorted = []
  result = []

  # 重みづけ機能
  upperclassman_id = list(map(lambda x: x[0], db.session.query(DebtorAttribute.member_id).filter(DebtorAttribute.group_session_id == session_id, DebtorAttribute.attribute == "先輩").all()))
  weight_money = int(round((0.2 * sum(amount)) / len(member_id), -2))
  for upperclassman in upperclassman_id:
    for member in member_id:
      if upperclassman != member:
        payer.append(member)
        debtor.append(upperclassman)
        amount.append(weight_money)

  #payNumに各メンバーの負担金を追加
  for member in member_id:
    for i in range (len(payer)):
      #支払った場合
      if member == payer[i]:
        money -= amount[i]
      #支払ってもらった場合
      elif member == debtor[i]:
        money += amount[i]
    payNum.append (money)
    money = 0

  #payment_dictに誰が何円損得しているのかを追加
  for j in range(len(member_id)):
    payment_dict[member_id[j]] = payNum[j]

  #払い足りない人と払いすぎている人をunderpaymentとoverpaymentに分ける
  for key, value in payment_dict.items():
    #払い足りない場合
    if value >= 0:
      underpayment[key] = value
    #払いすぎている場合
    else:
      overpayment[key] = value

  #金額の大きい順にソートし、underとoverを二次元配列に変換
  for ukey,uvalue in dict(sorted(underpayment.items(), key=lambda i: i[1], reverse=True)).items():
    underpayment_sorted.append([ukey, uvalue])
  for okey, ovalue in dict(sorted(overpayment.items(), key=lambda i: i[1])).items():
    overpayment_sorted.append([okey, ovalue])

  #金銭授受
  for overpay in overpayment_sorted:
    value = overpay[1] #最も払いすぎている金額
    underpayment_sorted.sort(key=lambda i: i[1], reverse=True)
    for num, underpay in enumerate(underpayment_sorted):
      pay_back = underpay[1] + value #その時点で最も足りていない人から払いすぎている人への支払い
      if pay_back >= 0: #払い足りない場合
        underpayment_sorted[num][1] = pay_back #支払う必要のある残額に更新
        result.append([underpay[0], overpay[0], int(Decimal(str((abs(value)))).quantize(Decimal('0'), rounding = ROUND_HALF_UP))])
        value = 0
        break
      else: #払い終えた場合
        value = pay_back
        result.append([underpay[0], overpay[0], int(Decimal(str(underpay[1])).quantize(Decimal('0'), rounding = ROUND_HALF_UP))])
        underpayment_sorted[num][1] = 0 #支払う必要のある残額を0に
        continue
  
  result.sort(key=lambda i: i[2], reverse=True)
  result = [i for i in result if i[2] != 0] # 支払額が0のときは削除
  return result

# pay_off関数の結果から返答のメッセージを作成
def pay_off_data_to_string(pay_off_result_user_id, group_id):
  id_name_dict = payment_info.get_group_member_info(group_id)
  pay_off_result_list = list(map(lambda x: [id_name_dict[x[0]], id_name_dict[x[1]], x[2]], pay_off_result_user_id))

  pay_off_message_list = [f"{one_pay_off_result[0]}が{one_pay_off_result[1]}に{one_pay_off_result[2]}円払う\n" for one_pay_off_result in pay_off_result_list]
  pay_off_message = ("精算結果\n" + "".join(pay_off_message_list)).strip()

  return pay_off_message