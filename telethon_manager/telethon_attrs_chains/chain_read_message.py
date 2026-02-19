def get_msg_read_attr_chains():
    attrs_chains = {
        # MessageRead
        "read_message": {
            "event_outbox": "outbox",
            "event_contents": "contents",
            "event_max_id": "max_id",
            "event_original_update": "original_update",
            "event_original_update_peer": "original_update.peer",
            "event_original_update_pts": "original_update.pts",
            "event_original_update_pts_count": "original_update.pts_count",
            "separator": "", },
        # Peer
        "original_update_peer": {
            "event_original_update_peer_channel_id": "original_update.peer.channel_id",
            "event_original_update_peer_chat_id": "original_update.peer.chat_id",
            "event_original_update_peer_user_id": "original_update.peer.user_id",
            "separator": "", },
    }
    return attrs_chains
