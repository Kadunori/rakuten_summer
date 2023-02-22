def get_group_summary(group_id,token):
    import repuests

    url = "https://api.line.me/v2/bot/group/" + group_id + "/summary"
    headers = {"channel access token":token}
    response = requests.post(url, headers=headers)
    print(response)