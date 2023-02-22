import re
from flask import Flask, request, abort
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os

from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, JoinEvent
)
from service.how_to_use import show_how_to_use

from repository.database import init_db
from repository.create_init import create_init
from service import group_service, payment_info, group_session_service
from service.fetcher import fetch_group_member_profile
from service.pay_off import pay_off, pay_off_data_to_string
from service.debtor_attribute_service import set_debtor_attribute


load_dotenv()

# CHANNEL_ACCESS_TOKEN
line_bot_api = LineBotApi(os.getenv('LINE_CHANNEL_ACCESS_TOKEN'))
# Pv2GVXFThSd/MYwKxi/olENWIas14h6ZsB9IOU8WLp92jqGKjTEyjZCwMgCUgh/bHoknZORnhIr38H75CtCC/RHKUBnuDDaITXP7yWOEggVFCYXO8fgcgOemmqa0QINsxgmiDcsPNEvwyEvWGHz2tQdB04t89/1O/w1cDnyilFU=
# CHANNEL_SECRET
handler = WebhookHandler(os.getenv('LINE_CHANNEL_SECRET'))
# 725a7eceaac2e8afe302e77f7b02daf4
app = Flask(__name__)
app.config.from_object("repository.config.Config")
init_db(app)
create_init(app)

# Flaskの実行自体がうまくいっているか動作を確かめるため（いらない）
@app.route("/")
def say_hello():
    return "Hello"


# LINE側に「こういうラインボットがあるよ～」って知らせる処理（呪文）
@app.route("/callback", methods=["POST"])
def callback():
    # リクエストヘッダーから署名検証のための値を取得
    signature = request.headers["X-Line-Signature"]

    # リクエストボディを取得
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        # 署名を検証し、問題なければhandleに定義されている関数を呼び出
        handler.handle(body, signature)
    except InvalidSignatureError:
        # 署名検証で失敗したときは例外をあげる
        print(
            "Invalid signature. Please check your channel access token/channel secret."
        )
        abort(400)

    return "OK"


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    message = event.message.text
    pay_user_id = event.source.user_id
    group_id = event.source.group_id
    word = message.split()
    if word[0] == "割り勘マン":
        if word[1].isdecimal() == True:
            user_profile = fetch_group_member_profile(group_id, pay_user_id)
            group_session_id = group_session_service.read_group_session_id(group_id)
            pay_session_id = payment_info.register_pay_info(
                word=word,
                pay_user_id=pay_user_id,
                pay_user_name=user_profile.display_name,
                current_group_id=group_id,
                group_session_id=group_session_id
            )
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=f"支払い登録完了\n支払いID: {pay_session_id}"),
            )

        elif word[1] == "修正":
            # 支払い削除関数（cancel_payment.py）を呼び出す
            line_bot_api.reply_message(
                event.reply_token, TextSendMessage(text="支払い情報修正処理")
            )
        elif word[0] == "削除":
            line_bot_api.reply_message(
                event.reply_token, TextSendMessage(text="支払い情報削除処理")
            )
        elif word[1] == "精算":
            group_session_id = group_session_service.read_group_session_id(group_id)
            pay_off_result_user_id = pay_off(group_id=group_id, session_id=group_session_id)

            result_message = pay_off_data_to_string(pay_off_result_user_id, group_id)
            
            # セッション更新
            group_session_service.register_group_session(group_id)

            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=result_message))

        elif word[1] == "精算キャンセル":
            line_bot_api.reply_message(
                event.reply_token, TextSendMessage(text="精算キャンセル処理")
            )
        elif word[1] == "使い方":
            text = str(show_how_to_use())
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=text))
        elif word[1] == "登録":
            if group_service.exist_user(pay_user_id, group_id):
                line_bot_api.reply_message(
                    event.reply_token, TextSendMessage(text="登録済みです")
                )
            else:
                user_profile = fetch_group_member_profile(group_id, pay_user_id)
                group_service.register_user(
                    pay_user_id, user_profile.display_name, group_id
                )
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text=f"{user_profile.display_name}さん　登録完了"),
                )
        elif word[1] == "先輩":
            user_profile = fetch_group_member_profile(group_id, pay_user_id)
            group_session_id = group_session_service.read_group_session_id(group_id)
            set_debtor_attribute(pay_user_id, group_session_id, "先輩")
            line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text=f"{user_profile.display_name}さんを先輩として登録しました"),
                )
        else:
            line_bot_api.reply_message(
                event.reply_token, TextSendMessage(text="そんなコマンドないよ")
            )
    else:
        pass

@handler.add(JoinEvent)
def handleJoin(event):
    group_id = event.source.group_id
    group_session_service.register_group_session(group_id)

if __name__ == "__main__":
    app.run()
