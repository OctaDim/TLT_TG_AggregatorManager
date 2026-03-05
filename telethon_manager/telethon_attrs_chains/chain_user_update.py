def get_user_update_attr_chains():
    attrs_chains = {
        # event_original_update
        "event_original_update": {
            "ev_orig_upd_channel_id": "original_update.channel_id",
            "ev_orig_upd_chat_id": "original_update.chat_id",
            "ev_orig_upd_user_id": "original_update.user_id",
            "ev_orig_upd_from_id": "original_update.from_id",  # (Peer)
            "ev_orig_upd_action": "original_update.action",
            "ev_orig_upd_top_msg_id": "original_update.top_msg_id",
            "separator": ""},
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
    }
    return attrs_chains
