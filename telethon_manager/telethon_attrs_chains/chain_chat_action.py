def get_chat_action_attr_chains():
    attrs_chains = {
        # action_message
        "action_message": {
            "action_message_id": "action_message.id",
            "action_message_peer_id": "action_message.peer_id",  # peer_id >>> (Peer)
            "action_message_date": "action_message.date",
            "action_message_action": "action_message.action",
            "action_message_out": "action_message.out",
            "action_message_mentioned": "action_message.mentioned",
            "action_message_media_unread": "action_message.media_unread",
            "action_message_reactions_are_possible": "action_message.reactions_are_possible",
            "action_message_silent": "action_message.silent",
            "action_message_post": "action_message.post",
            "action_message_legacy": "action_message.legacy",
            "action_message_from_id": "action_message.from_id",  # from_id >>> (Peer)
            "action_message_saved_peer_id": "action_message.saved_peer_id",
            "action_message_reply_to": "action_message.reply_to",
            "action_message_reactions": "action_message.reactions",
            "action_message_ttl_period": "action_message.ttl_period",
            "separator": "", },
        # stringify()
        "stringify": {
            "new_pin": "new_pin",
            "new_photo": "new_photo",
            "photo": "photo",
            "user_added": "user_added",
            "user_joined": "user_joined",
            "user_left": "user_left",
            "user_kicked": "user_kicked",
            "unpin": "unpin",
            "created": "created",
            "new_title": "new_title",
            "new_score": "new_score", },
        # peer_id >>> (Peer)
        "action_message_peer_id": {
            "action_message_peer_id_channel_id": "action_message.peer_id.channel_id",
            "action_message_peer_id_chat_id": "action_message.peer_id.chat_id",
            "action_message_peer_id_user_id": "action_message.peer_id.user_id",
            "separator": "", },
        # from_id >>> (Peer)
        "action_message_from_id": {
            "action_message_from_id_channel_id": "action_message.from_id.channel_id",
            "action_message_from_id_chat_id": "action_message.from_id.chat_id",
            "action_message_from_id_user_id": "action_message.from_id.user_id",
            "separator": "", },
        # action_message >>> action
        "action_message >>> action": {
            "action_message_action_users": "action_message.action.users", },
        # Peer
        "original_update_message": {
            "event_original_update_pts": "original_update.pts",
            "event_original_update_pts_count": "original_update.pts_count",
            "event_original_update_peer_user_id": "original_update.peer.user_id",
            "separator": "", },
    }
    return attrs_chains
