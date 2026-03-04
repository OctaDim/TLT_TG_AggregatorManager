def get_user_update_attr_chains():
    attrs_chains = {
        # event__client
        "event__client": {
            "ev__client": "_client",
            "separator": ""},
        # event stringify
        "event stringify": {
            "ev_user_id": "user_id",
            "ev_status": "status",
            "ev_status_expires": "status.expires",
            "ev_status_was_online": "status.was_online",
            "ev_action": "action",
            "ev_chat": "chat",
            "ev__chat": "_chat",
            "ev_chat_id": "chat_id",
            # "ev_chat__client": "_client",
            "separator": ""},



        # event_sender (Sender) ?????????????????
        "event_sender": {
            "tlt_sender": "sender",
            "tlt_sender_id": "sender.id",
            "tlt_sender_username": "sender.username",
            "tlt_sender_first_name": "sender.first_name",
            "tlt_sender_last_name": "sender.last_name",
            "tlt_sender_phone": "sender.phone",
            "tlt_sender_bot": "sender.bot",
            "separator": ""},
        # chat >>> (Chat) ?????????????????
        "event_chat": {
            "ev_chat_title": "chat.title",
            "separator": ""},
    }
    return attrs_chains
