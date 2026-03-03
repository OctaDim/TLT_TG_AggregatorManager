def get_chat_action_attr_chains():
    attrs_chains = {
        # event_original_update
        "original_update_message": {
            "ev_orig_upd_pts": "original_update.pts",
            "ev_orig_upd_pts_count": "original_update.pts_count",
            "ev_orig_upd_message": "original_update.message",
            "ev_orig_upd_message_action": "original_update.message.action",  # ev_original_update_message_action
            "separator": ""},
        # event__client
        "event__client": {
            "ev__client": "_client",
            "separator": ""},
        # event stringify()
        "event stringify": {
            "ev_act_msg": "action_message",  # event_action_message >>> (MessageService)
            "ev_orig_upd": "original_update",  # event_original_update >>> (UpdateNewMessage)
            "ev_new_pin": "new_pin",
            "ev_new_photo": "new_photo",
            "ev_photo": "photo",
            "ev_user_added": "user_added",
            "ev_user_joined": "user_joined",
            "ev_user_left": "user_left",
            "ev_user_kicked": "user_kicked",
            "ev_unpin": "unpin",
            "ev_created": "created",
            "ev_new_title": "new_title",
            "ev_new_score": "new_score",
            "separator": ""},
        # event_action_message >>> (MessageService)
        "event_action_message": {
            "ev_act_msg_id": "action_message.id",
            "ev_act_msg_peer_id": "action_message.peer_id",  # ev_action_message_peer_id >>> (Peer)
            "ev_act_msg_date": "action_message.date",
            "ev_act_msg_action": "action_message.action",  # ev_action_message_action >>> ()
            "ev_act_msg_action_users": "action_message.action.users",
            "ev_act_msg_action_user_id": "action_message.action.user_id",
            "ev_act_msg_out": "action_message.out",
            "ev_act_msg_mentioned": "action_message.mentioned",
            "ev_act_msg_media_unread": "action_message.media_unread",
            "ev_act_msg_reactions_are_possible": "action_message.reactions_are_possible",
            "ev_act_msg_silent": "action_message.silent",
            "ev_act_msg_post": "action_message.post",
            "ev_act_msg_legacy": "action_message.legacy",
            "ev_act_msg_from_id": "action_message.from_id",  # ev_action_message_from_id >>> (Peer)
            "ev_act_msg_saved_peer_id": "action_message.saved_peer_id",  # ev_action_message_saved_peer_id >>> (Peer)
            "ev_act_msg_reply_to": "action_message.reply_to",
            "ev_act_msg_reactions": "action_message.reactions",
            "ev_act_msg_ttl_period": "action_message.ttl_period",
            "separator": ""},
        # ev_action_message_peer_id >>> (Peer)
        "ev_action_message_peer_id": {
            "ev_act_msg_peer_id_channel_id": "action_message.peer_id.channel_id",
            "ev_act_msg_peer_id_chat_id": "action_message.peer_id.chat_id",
            "ev_act_msg_peer_id_user_id": "action_message.peer_id.user_id",
            "separator": ""},
        # ev_action_message_from_id >>> (Peer)
        "ev_action_message_from_id": {
            "ev_act_msg_from_id_channel_id": "action_message.from_id.channel_id",
            "ev_act_msg_from_id_chat_id": "action_message.from_id.chat_id",
            "ev_act_msg_from_id_user_id": "action_message.from_id.user_id",
            "separator": ""},
        # ev_action_message_saved_peer_id >>> (Peer)
        "ev_action_message_saved_peer_id": {
            "ev_act_msg_saved_peer_id_channel_id": "action_message.saved_peer_id.channel_id",
            "ev_act_msg_saved_peer_id_chat_id": "action_message.saved_peer_id.chat_id",
            "ev_act_msg_saved_peer_id_user_id": "action_message.saved_peer_id.user_id",
            "separator": ""},
        # ev_action_message_action (MessageActionChatAddUser, MessageActionChatDeleteUser)
        "ev_action_message_action": {
            #     "ev_action_message_action_users": "action_message.action.users",  # No access!!!
            #     "ev_action_message_action_user_id": "action_message.action.user_id",
            "separator": ""},
        # ev_original_update_message_action >>> (MessageActionChatAddUser, MessageActionChatDeleteUser)
        "ev_original_update_message_action": {
            "ev_orig_upd_message_action_users": "original_update.message.action.users",
            "ev_orig_upd_message_action_user_id": "original_update.message.action.user_id",
            "separator": ""},
        # event additional
        "event additional": {
            "ev_is_private": "is_private",
            "ev_is_group": "is_group",
            "ev_is_channel": "is_channel",
            "ev_chat": "chat",
            "ev_chat_id": "chat_id",
            "ev_chat__client": "_client",
            "separator": ""},
        # chat >>> (Chat)
        "event_chat": {
            "ev_chat_title": "chat.title",
            "separator": ""},
    }
    return attrs_chains
