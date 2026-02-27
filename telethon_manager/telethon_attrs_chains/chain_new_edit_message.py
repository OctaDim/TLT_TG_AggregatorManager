def get_event_new_edit_msg_attr_chains():
    attrs_chains = {
        # event_original_update
        "event_original_update": {
            "ev_original_update_pts": "original_update.pts",
            "ev_original_update_pts_count": "original_update.pts_count",
            "separator": ""},
        # event__client
        "event__client": {
            "ev__client": "_client",
            "separator": ""},
        # event stringify()
        "event stringify": {
            "ev_id": "id",
            "ev_peer_id": "peer_id",  # ev_peer_id >>> (Peer)
            "ev_date": "date",
            "ev_edit_date": "edit_date",
            "ev_out": "out",
            "ev_mentioned": "mentioned",
            "ev_media_unread": "media_unread",
            "ev_silent": "silent",
            "ev_post": "post",
            "ev_from_scheduled": "from_scheduled",
            "ev_legacy": "legacy",
            "ev_edit_hide": "edit_hide",  # ???
            "ev_pinned": "pinned",
            "ev_noforwards": "noforwards",
            "ev_invert_media": "invert_media",
            "ev_offline": "offline",
            "ev_video_processing_pending": "video_processing_pending",
            "ev_paid_suggested_post_stars": "paid_suggested_post_stars",
            "ev_paid_suggested_post_ton": "paid_suggested_post_ton",
            "ev_from_id": "from_id",  # ev_from_id >>> (Peer)
            "ev_from_boosts_applied": "from_boosts_applied",
            "ev_saved_peer_id": "saved_peer_id",
            "ev_fwd_from": "fwd_from",  # ev_fwd_from >>> (MessageFwdHeader)
            "ev_via_bot_id": "via_bot_id",
            "ev_via_business_bot_id": "via_business_bot_id",
            "ev_reply_to": "reply_to",  # ev_reply_to >>> (MessageReplyHeader)
            "ev_media": "media",  # ev_media >>>,
            "ev_reply_markup": "reply_markup",
            "ev_entities": "entities",
            "ev_views": "views",
            "ev_forwards": "forwards",
            "ev_replies": "replies",  # ev_repliers >>> (MessageReplies)
            "ev_post_author": "post_author",
            "ev_grouped_id": "grouped_id",
            "ev_reactions": "reactions",  # ev_reactions >>> (MessageReactions)
            "ev_restriction_reason": "restriction_reason",
            "ev_ttl_period": "ttl_period",
            "ev_quick_reply_shortcut_id": "quick_reply_shortcut_id",
            "ev_effect": "effect",
            "ev_factcheck": "factcheck",
            "ev_report_delivery_until_date": "report_delivery_until_date",
            "ev_paid_stars": "paid_stars",
            "ev_suggested_post": "suggested_post",
            "separator": ""},
        # event additional
        "event additional": {
            "ev_file": "file",
            "ev_broadcast": "broadcast",  # ???
            "ev_is_reply": "is_reply",
            "ev_is_private": "is_private",
            "ev_is_group": "is_group",
            "ev_is_channel": "is_channel",
            "ev_chat": "chat",  # chat >>> (Chat)
            "ev_chat_id": "chat_id",
            "ev_chat__client": "_client",
            "ev_sender_id": "sender_id",
            "ev_forward": "forward",
            "ev_photo": "photo",
            "ev_document": "document",
            "ev_audio": "audio",
            "ev_video": "video",
            "ev_voice": "voice",
            "ev_sticker": "sticker",
            "ev_contact": "contact",
            "ev_location": "location",
            "ev_venue": "venue",
            "ev_game": "game",
            "ev_poll": "poll",
            "ev_dice": "dice",
            "ev_invoice": "invoice",
            "ev_web_preview": "web_preview",
            "ev_action": "action",
            "ev_changed_media": "changed_media",  # ???
            "ev_changed_text": "changed_text",  # ???
            "ev_changed_markup": "changed_markup",  # ???
            "ev_changed_entities": "changed_entities",  # ???
            "separator": ""},
        # event__client (event__text, event__file)
        "event__client (__text, __file)": {
            "ev__client": "_client",
            # "ev__text": "_text",  # From another parameter
            # "ev__file": "_file",  # From another parameter
            "separator": ""},
        # event_peer_id >>> (Peer)
        "event_peer_id": {
            "ev_peer_id_channel_id": "peer_id.channel_id",
            "ev_peer_id_chat_id": "peer_id.chat_id",
            "ev_peer_id_user_id": "peer_id.user_id",
            "separator": ""},
        # event_from_id >>> (Peer)
        "event_from_id": {
            "ev_from_id_channel_id": "from_id.channel_id",
            "ev_from_id_chat_id": "from_id.chat_id",
            "ev_from_id_user_id": "from_id.user_id",
            "separator": ""},
        # event_fwd_from >>> (MessageFwdHeader)
        "event_fwd_from": {
            "ev_fwd_from_date": "fwd_from.date",
            "ev_fwd_from_from_id": "fwd_from.from_id",  # ev_fwd_from_from_id_peer_id >>> (Peer)
            "ev_fwd_from_from_name": "fwd_from.from_name",
            "ev_fwd_from_channel_post": "fwd_from.channel_post",
            "ev_fwd_from_post_author": "fwd_from.post_author",
            "ev_fwd_from_saved_from_peer": "fwd_from.saved_from_peer",
            "ev_fwd_from_saved_from_msg_id": "fwd_from.saved_from_msg_id",
            "separator": ""},
        # ev_fwd_from_from_id_peer_id >>> (Peer)
        "ev_fwd_from_from_id_peer_id": {
            "ev_fwd_from_from_id_channel_id": "fwd_from.from_id.channel_id",
            "ev_fwd_from_from_id_chat_id": "fwd_from.from_id.chat_id",
            "ev_fwd_from_from_id_user_id": "fwd_from.from_id.user_id",
            "separator": ""},
        # event_reply_to >>> (MessageReplyHeader)
        "event_reply_to": {
            "ev_reply_to_reply_to_msg_id": "reply_to.reply_to_msg_id",
            "ev_reply_to_reply_to_peer_id": "reply_to.reply_to_peer_id",  # Peer
            "ev_reply_to_reply_to_top_id": "reply_to.reply_to_top_id",
            "ev_reply_to_reply_to_scheduled": "reply_to.reply_to_scheduled",
            "ev_reply_to_forum_topic": "reply_to.forum_topic",
            "ev_reply_to_quote": "reply_to.quote",
            "ev_reply_to_quote_text": "reply_to.quote_text",
            "ev_reply_to_reply_media": "reply_to.reply_media",
            "ev_reply_to_todo_item_id": "reply_to.todo_item_id",
            "separator": ""},
        # ev_reply_to_reply_to_peer_id >>> (Peer)
        "ev_reply_to_reply_to_peer_id": {
            "ev_reply_to_reply_to_peer_id_channel_id": "reply_to.reply_to_peer_id.channel_id",
            "ev_reply_to_reply_to_peer_id_chat_id": "reply_to.reply_to_peer_id.chat_id",
            "ev_reply_to_reply_to_peer_id_user_id": "reply_to.reply_to_peer_id.user_id",
            "separator": ""},
        # event_media >>> photo (MessageMediaPhoto)
        "event_media_photo": {
            "ev_media_photo": "media.photo",  # Photo >>>
            "ev_media_photo_ttl_seconds": "media.ttl_seconds",
            # (Photo)
            "ev_media_photo_id": "media.photo.id",
            "ev_media_photo_access_hash": "media.photo.access_hash",
            "ev_media_photo_file_reference": "media.photo.file_reference",
            "ev_media_photo_date": "media.photo.date",
            "ev_media_photo_sizes": "media.photo.sizes",  # PhotoSize
            "ev_media_video_sizes": "media.photo.sizes",  # VideoSize
            "ev_media_photo_has_stickers": "media.photo.has_stickers",
            "separator": ""},
        # event_media_document >>> (MessageMediaDocument)
        "event_media_document": {
            "ev_media_document": "media.document",  # Document >>>
            "ev_media_document_ttl_seconds": "media.ttl_seconds",
            # (Document)
            "ev_media_document_id": "media.document.id",
            "ev_media_document_access_hash": "media.document.access_hash",
            "ev_media_document_file_reference": "media.document.file_reference",
            "ev_media_document_date": "media.document.date",
            "ev_media_document_mime_type": "media.document.mime_type",
            "ev_media_document_size": "media.document.size",
            "ev_media_document_thumbs": "media.document.thumbs",  # List[PhotoSize]
            "ev_media_document_video_thumbs": "media.document.video_thumbs",  # List[VideoSize]
            "ev_media_document_attributes": "media.document.attributes",  # List[DocumentAttribute]
            "separator": ""},
        # event_media_geo >>> geo (MessageMediaGeo)
        "event_media_geo": {
            "ev_media_geo_geo": "media.geo",  # GeoPoint >>>
            "separator": ""},
        # event_media_geo >>> geo_live (MessageMediaGeoLive)
        "event_media_geo_geo_live": {
            "ev_media_geo_live_geo": "media.geo",  # GeoPoint
            "ev_media_heading": "media.heading",
            "ev_media_period": "media.period",
            "ev_media_proximity_notification_radius": "media.proximity_notification_radius",
            "separator": ""},
        # event_media >>> venue (MessageMediaVenue)
        "event_media_venue": {
            "ev_media_venue_geo": "media.geo",  # GeoPoint >>>
            "ev_media_title": "media.title",
            "ev_media_address": "media.address",
            "ev_media_provider": "media.provider",
            "ev_media_venue_id": "media.venue_id",
            "ev_media_venue_type": "media.venue_type",
            "separator": ""},
        # event_media >>> contact (MessageMediaContact)
        "event_media_contact": {
            "ev_media_phone_number": "media.phone_number",
            "ev_media_first_name": "media.first_name",
            "ev_media_last_name": "media.last_name",
            "ev_media_vcard": "media.vcard",
            "separator": ""},
        # event_media >>> poll (Poll)
        "event_media_poll": {
            "ev_media_poll": "media.poll",  # Poll >>>
            "ev_media_results": "media.results",
            "separator": ""},
        # event_media >>> dice (MessageMediaDice)
        "event_media_dice": {
            "ev_media_value": "media.value",
            "ev_media_emoticon": "media.emoticon",
            "separator": ""},
        # event_media >>> game (MessageMediaGame)
        "event_media_game": {
            "ev_media_game": "media.game",  # Game >>>
            "separator": ""},
        # event_media >>> invoice (MessageMediaInvoice)
        "event_media_invoice": {
            "ev_media_invoice": "media.invoice",  # Invoice >>>
            "separator": ""},
        # event_media >>> webpage (MessageMediaWebPage)
        "event_media_webpage": {
            "ev_media_webpage": "media.webpage",  # WebPage
            "separator": ""},
        # event_repliers (MessageReplies)
        "event_replies": {
            "ev_replies_replies": "replies.replies",
            "ev_replies_replies_pts": "replies.replies_pts",
            "ev_replies_comments": "replies.comments",
            "ev_replies_recent_repliers": "replies.recent_repliers",
            "ev_replies_channel_id": "replies.channel_id",
            "ev_replies_max_id": "replies.max_id",
            "ev_replies_read_max_id": "replies.read_max_id",
            "separator": ""},
        # event_reactions >>> (MessageReactions)
        "event_reactions": {
            "ev_reactions_results": "reactions.results",  # List[ReactionCount]
            "ev_reactions_min": "reactions.min",
            "ev_reactions_can_see_list": "reactions.can_see_list",
            "ev_reactions_reactions_as_tags": "reactions.reactions_as_tags",
            "ev_reactions_recent_reactions": "reactions.recent_reactions",  # List[MessagePeerReaction]
            "ev_reactions_top_reactors": "reactions.top_reactors",  # List[Peer]
            "separator": ""},
        # event_file (File)
        "event_file": {
            "ev_file_id": "file.id",
            "ev_file_name": "file.name",
            "ev_file_size": "file.size",
            "ev_file_date": "file.date",
            "ev_file_mime_type": "file.mime_type",
            "separator": ""},
        # event_sender (Sender)
        "event_sender": {
            "ev_sender_id": "sender.id",
            "ev_sender_username": "sender.username",
            "ev_sender_first_name": "sender.first_name",
            "ev_sender_last_name": "sender.last_name",
            "ev_sender_bot": "sender.bot",
            "separator": ""},
        # chat >>> (Chat)
        "event_chat": {
            "ev_chat_title": "chat.title",
            "separator": ""},
    }
    return attrs_chains
