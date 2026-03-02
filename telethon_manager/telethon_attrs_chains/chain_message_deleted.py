def get_msg_delete_attr_chains():
    attrs_chains = {
        # event_original_update
        "delete_message": {
            "ev_orig_upd_messages": "original_update.messages",
            "ev_orig_upd_pts": "original_update.pts",
            "ev_orig_upd_pts_count": "original_update.pts_count",
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
            "ev_is_private": "is_private",  # Always None???
            "ev_is_group": "is_group",
            "ev_is_channel": "is_channel",
            "ev_chat": "chat",  # Always None???
            "ev_chat_id": "chat_id",  # Always None???
            "ev_chat__client": "_client",
            "separator": ""},
        # event_original_update >>> (Peer)
        "original_update_peer": {
            # "ev_orig_upd_peer_channel_id": "original_update.peer.channel_id",  # Always None???
            # "ev_orig_upd_peer_chat_id": "original_update.peer.chat_id",  # Always None???
            # "ev_orig_upd_peer_user_id": "original_update.peer.user_id",  # Always None???
            "separator": ""},
    }
    return attrs_chains
