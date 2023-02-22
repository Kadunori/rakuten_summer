from linebot import LineBotApi
import os
from dotenv import load_dotenv


load_dotenv()
line_bot_api = LineBotApi(os.getenv('LINE_CHANNEL_ACCESS_TOKEN'))


def fetch_group_member_profile(group_id, user_id):
    profile = line_bot_api.get_group_member_profile(group_id, user_id)
    return profile