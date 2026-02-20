def get_msg_delete_attr_chains():
    attrs_chains = {
        # event_original_update
        "delete_message": {
            "ev_original_update_messages": "original_update.messages",
            "ev_original_update_pts": "original_update.pts",
            "ev_original_update_pts_count": "original_update.pts_count",
            "separator": ""},
        # event__client
        "event__client": {
            "ev__client": "_client",
            "separator": ""},
        # event stringify()
        "event stringify": {
            "ev_deleted_id": "deleted_id",
            "ev_deleted_ids": "deleted_ids",
            "separator": ""},
        # event additional
        "event additional": {
            "ev_is_private": "is_private",  # ???
            "ev_is_group": "is_group",
            "ev_is_channel": "is_channel",
            "ev_chat": "chat",  # ???
            "ev_chat_id": "chat_id",  # ???
            "ev_chat__client": "_client",
            "separator": ""},
        # event_original_update >>> (Peer)
        "original_update_peer": {
            "ev_original_update_peer_channel_id": "original_update.peer.channel_id",  # ???
            "ev_original_update_peer_chat_id": "original_update.peer.chat_id",  # ???
            "ev_original_update_peer_user_id": "original_update.peer.user_id",  # ???
            "separator": ""},
    }
    return attrs_chains
