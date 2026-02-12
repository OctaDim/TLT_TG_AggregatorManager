from telethon import events, TelegramClient

from telethon_manager.telethon_client_config import TelethonConfig
from utils_common.clean_str_new_lines_spaces import clean_text
from utils_common.get_obj_attrs_vals_by_attr_chain import (
    get_attr_value_by_attr_chain, get_attrs_values_by_attr_chains)


async def new_message_handler_helper(
        event: events.NewMessage.Event,
        telethon_client: TelegramClient,
        telethon_config: TelethonConfig
) -> None:
    if None in (telethon_client, telethon_config):
        print(f"Deleted Telethon object(s), not handled event [ERROR]:\n"
              f"telethon_client: {telethon_client}\n"
              f"telethon_config: {telethon_config}\n")
        return
    # print(event.stringify())

    attrs_chains = {
        "event_message_id": "message.id",
        "event_message_peer_id": "message.peer_id",  # peer_id >>> (Peer)
        "event_message_date": "message.date",
        "event_message_edit_date": "message.edit_date",
        "event_message_file": "message.file",
        "event_message_out": "message.out",
        "event_message_is_reply": "message.is_reply",
        "event_message_is_private": "message.is_private",
        "event_message_is_group": "message.is_group",
        "event_message_is_channel": "message.is_channel",
        "event_message_chat_id": "message.chat_id",
        "event_message_sender_id": "message.sender_id",
        "event_message_message_id": "message.message_id",
        "event_message_hide_edit": "message.hide_edit",
        "event_message_forward": "message.forward",
        "event_message_photo": "message.photo",
        "event_message_document": "message.document",
        "event_message_audio": "message.audio",
        "event_message_video": "message.video",
        "event_message_voice": "message.voice",
        "event_message_sticker": "message.sticker",
        "event_message_contact": "message.contact",
        "event_message_location": "message.location",
        "event_message_venue": "message.venue",
        "event_message_game": "message.game",
        "event_message_poll": "message.poll",
        "event_message_dice": "message.dice",
        "event_message_invoice": "message.invoice",
        "event_message_web_preview": "message.web_preview",
        "event_message_action": "message.action",
        "event_message_changed_media": "message.changed_media",
        "event_message_changed_text": "message.changed_text",
        "event_message_changed_markup": "message.changed_markup",
        "event_message_changed_entities": "message.changed_entities",
        "empty_0": "___",

        "event_message_mentioned": "message.mentioned",
        "event_message_media_unread": "message.media_unread",
        "event_message_silent": "message.silent",
        "event_message_edit_hide": "message.edit_hide",
        "event_message_post": "message.post",
        "event_message_from_scheduled": "message.from_scheduled",
        "event_message_pinned": "message.pinned",
        "event_message_noforwards": "message.noforwards",
        "event_message_offline": "message.offline",
        "event_message_video_processing_pending": "message.video_processing_pending",
        "event_message_paid_suggested_post_stars": "message.paid_suggested_post_stars",
        "event_message_paid_suggested_post_ton": "message.paid_suggested_post_ton",
        "event_message_from_id": "message.from_id",  # from_id >>> (Peer)
        "event_message_from_boosts_applied": "message.from_boosts_applied",
        "event_message_saved_peer_id": "message.saved_peer_id",
        "event_message_fwd_from": "message.fwd_from",  # fwd_from >>> (MessageFwdHeader)
        "event_message_via_bot_id": "message.via_bot_id",
        "event_message_via_business_bot_id": "message.via_business_bot_id",
        "event_message_reply_to": "message.reply_to",  # reply_to >>> (MessageReplyHeader)
        "event_message_media": "message.media",  # media >>>,
        "event_message_entities": "message.entities",
        "event_message_views": "message.views",
        "event_message_forwards": "message.forwards",
        "event_message_replies": "message.replies",  # repliers >>> (MessageReplies)
        "event_message_post_author": "message.post_author",
        "event_message_grouped_id": "message.grouped_id",
        "event_message_reactions": "message.reactions",  # reactions >>> (MessageReactions)
        "event_message_restriction_reason": "message.restriction_reason",
        "event_message_ttl_period": "message.ttl_period",
        "event_message_paid_message_stars": "message.paid_message_stars",
        "event_message_suggested_post": "message.suggested_post",
        "event_message__client": "message._client",
        "event_message__text": "message._text",
        "event_message__file": "message._file",
        "empty_1": "___",

        # peer_id >>> (Peer)
        "event_message_peer_id_channel_id": "message.peer_id.channel_id",
        "event_message_peer_id_chat_id": "message.peer_id.chat_id",
        "event_message_peer_id_user_id": "message.peer_id.user_id",
        "empty_2": "___",

        # from_id >>> (Peer)
        "event_message_from_id_channel_id": "message.from_id.channel_id",
        "event_message_from_id_chat_id": "message.from_id.chat_id",
        "event_message_from_id_user_id": "message.from_id.user_id",
        "empty_3": "___",

        # fwd_from >>> (MessageFwdHeader)
        "event_message_fwd_from_date": "message.fwd_from.date",
        "event_message_fwd_from_from_id": "message.fwd_from.from_id",  # Peer
        "event_message_fwd_from_from_name": "message.fwd_from.from_name",
        "event_message_fwd_from_channel_post": "message.fwd_from.channel_post",
        "event_message_fwd_from_post_author": "message.fwd_from.post_author",
        "event_message_fwd_from_saved_from_peer": "message.fwd_from.saved_from_peer",
        "event_message_fwd_from_saved_from_msg_id": "message.fwd_from.saved_from_msg_id",
        "empty_4": "___",

        # reply_to >>> (MessageReplyHeader)
        "event_message_reply_to_reply_to_msg_id": "message.reply_to.reply_to_msg_id",
        "event_message_reply_to_reply_to_peer_id": "message.reply_to.reply_to_peer_id",  # Peer
        "event_message_reply_to_reply_to_top_id": "message.reply_to.reply_to_top_id",
        "event_message_reply_to_reply_to_scheduled": "message.reply_to.reply_to_scheduled",
        "event_message_reply_to_forum_topic": "message.reply_to.forum_topic",
        "event_message_reply_to_quote": "message.reply_to.quote",
        "event_message_reply_to_quote_text": "message.reply_to.quote_text",
        "event_message_reply_to_reply_media": "message.reply_to.reply_media",
        "event_message_reply_to_todo_item_id": "message.reply_to.todo_item_id",
        "empty_5": "___",

        # media >>>
        # photo (MessageMediaPhoto)
        "event_message_media_photo": "message.media.photo",  # Photo >>>
        "event_message_media_photo_ttl_seconds": "message.media.ttl_seconds",
        # Photo >>>
        "event_message_media_photo_id": "message.media.photo.id",
        "event_message_media_photo_access_hash": "message.media.photo.access_hash",
        "event_message_media_photo_file_reference": "message.media.photo.file_reference",
        "event_message_media_photo_date": "message.media.photo.date",
        "event_message_media_photo_sizes": "message.media.photo.sizes",  # PhotoSize
        "event_message_media_photo_has_stickers": "message.media.photo.has_stickers",
        "empty_6": "___",

        # document (MessageMediaDocument)
        "event_message_media_document": "message.media.document",  # Document >>>
        "event_message_media_document_ttl_seconds": "message.media.ttl_seconds",
        # Document >>>
        "event_message_media_document_id": "message.media.document.id",
        "event_message_media_document_access_hash": "message.media.document.access_hash",
        "event_message_media_document_file_reference": "message.media.document.file_reference",
        "event_message_media_document_date": "message.media.document.file_reference",
        "event_message_media_document_mime_type": "message.media.document.mime_type",
        "event_message_media_document_size": "message.media.document.size",
        "event_message_media_document_thumbs": "message.media.document.thumbs",  # List[PhotoSize]
        "event_message_media_document_video_thumbs": "message.media.document.video_thumbs",  # List[VideoSize]
        "event_message_media_document_attributes": "message.media.document.attributes",  # List[DocumentAttribute]
        "event_message_media_document_": "message.media.document.",

        "empty_7": "___",
        # geo (MessageMediaGeo)
        "event_message_media_geo_geo": "message.media.geo",  # GeoPoint
        # geo_live (MessageMediaGeoLive)
        "event_message_media_geo_live_geo": "message.media.geo",  # GeoPoint
        "event_message_media_heading": "message.media.heading",
        "event_message_media_period": "message.media.period",
        "event_message_media_proximity_notification_radius": "message.media.proximity_notification_radius",
        "empty_8": "___",
        # venue (MessageMediaVenue)
        "event_message_media_venue_geo": "message.media.geo",  # GeoPoint
        "event_message_media_title": "message.media.title",
        "event_message_media_address": "message.media.address",
        "event_message_media_provider": "message.media.provider",
        "event_message_media_venue_id": "message.media.venue_id",
        "event_message_media_venue_type": "message.media.venue_type",
        "empty_9": "___",
        # contact (MessageMediaContact)
        "event_message_media_phone_number": "message.media.phone_number",
        "event_message_media_first_name": "message.media.first_name",
        "event_message_media_last_name": "message.media.last_name",
        "event_message_media_vcard": "message.media.vcard",
        "empty_10": "___",
        # poll
        "event_message_media_poll": "message.media.poll",  # Poll
        "event_message_media_results": "message.media.results",
        "empty_11": "___",
        # dice (MessageMediaDice)
        "event_message_media_value": "message.media.value",
        "event_message_media_emoticon": "message.media.emoticon",
        # game (MessageMediaGame)
        "event_message_media_game": "message.media.game",  # Game
        # invoice (MessageMediaInvoice)
        # webpage (MessageMediaWebPage)
        "event_message_media_webpage": "message.media.webpage",  # WebPage
        "empty_12": "___",

        # repliers (MessageReplies)
        "event_message_replies_replies": "message.replies.replies",
        "event_message_replies_comments": "message.replies.comments",
        "event_message_replies_recent_repliers": "message.replies.recent_repliers",
        "event_message_replies_channel_id": "message.replies.channel_id",
        "event_message_replies_max_id": "message.replies.max_id",
        "event_message_replies_read_max_id": "message.replies.read_max_id",
        "empty_13": "___",

        # reactions >>> (MessageReactions)
        "event_message_reactions_results": "message.reactions.results",  # List[ReactionCount]
        "event_message_reactions_min": "message.reactions.min",
        "event_message_reactions_can_see_list": "message.reactions.can_see_list",
        "event_message_reactions_reactions_as_tags": "message.reactions.reactions_as_tags",
        "event_message_reactions_recent_reactions": "message.reactions.recent_reactions",  # List[MessagePeerReaction]
        "event_message_reactions_top_reactors": "message.reactions.top_reactors",  # List[Peer]
        "empty_14": "___",
        "empty_15": "___",

        # "event_peer_id": "peer_id",
        # "event_sender_id": "sender_id",
        # "event_from_id": "from_id",
        # "event_dlg_msg_id": "id",
        # "event_date": "date",
        # "event_edit_date": "edit_date",
        # "event_out": "out",
        # "event_is_reply": " is_reply",
        # "event_is_private": "is_private",
        # "event_is_group": "is_group",
        # "event_is_channel": "is_channel",
        # "event_views": "views",
        # "event_forwards": "forwards",
        # "event_replies": "replies",
        # "event_mentioned": "mentioned",
        # "event_post": "post",
        # "event_post_author": "post_author",
        # "event_noforwards": "noforwards",
        # "event_silent": "silent",
        # "event_scheduled": "scheduled",
        # "event_from_scheduled": "from_scheduled",
        # "event_media": "media",
        # "event_file": "file",
        # "event_photo": "photo",
        # "event_document": "document",
        # "event_audio": "audio",
        # "event_video": "video",
        # "event_voice": "voice",
        # "event_sticker": "sticker",
        # "event_contact": "contact",
        # "event_location": "location",
        # "event_venue": "venue",
        # "event_poll": "poll",
        # "event_game": "game",
        # "event_dice": "dice",
        # "event_invoice": "invoice",
        # "event_web_preview": "web_preview",
        # "event_action": "action",
        # "event_video_note": "video_note",
        # "event_gif": "gif",
        # "event_message": "message",
        # "event_paid_suggested_post_stars": "paid_suggested_post_stars",
        # "event_paid_suggested_post_ton": "paid_suggested_post_ton",
        # "event_via_bot_id": "via_bot_id",
        # "event_via_business_bot_id": "via_business_bot_id",
        # "event_reply_to_msg_id": "reply_to_msg_id",
        # "event_reply_to_peer_id": "reply_to_peer_id",
        # "event_reply_to_top_id": "reply_to_top_id",
        # "event_reply_to_scheduled": "reply_to_scheduled",
        # "event_forum_topic": "forum_topic",
        # "event_quote": "quote",
        # "event_quote_text": "quote_text",
        # "event_reply_from": "reply_from",
        # "event_reply_media": " reply_media",
        # "event_todo_item_id": "todo_item_id",
        # "event_forward": "forward",
        # "event_reactions": "reactions",
    }

    new_msg_evnt_params = await get_attrs_values_by_attr_chains(
        base_class_or_obj=event,
        attributes_chains_dict=attrs_chains)

    evnt_message_message = await get_attr_value_by_attr_chain(
        base_class_or_obj=event,
        attribute_chain="message.message")
    evnt_message_message = await clean_text(
        origin_text=evnt_message_message,
        clean_line_breaks=True,
        clean_continuous_spaces=True)
    new_msg_evnt_params["evnt_message_message"] = evnt_message_message

    evnt_message_text = await get_attr_value_by_attr_chain(
        base_class_or_obj=event,
        attribute_chain="message.text")
    evnt_message_text = await clean_text(
        origin_text=evnt_message_text,
        clean_line_breaks=True,
        clean_continuous_spaces=True)
    new_msg_evnt_params["evnt_message_text"] = evnt_message_text

    evnt_message_raw_text = await get_attr_value_by_attr_chain(
        base_class_or_obj=event,
        attribute_chain="message.raw_text")
    evnt_message_text = await clean_text(origin_text=evnt_message_raw_text,
                                         clean_line_breaks=True,
                                         clean_continuous_spaces=True)
    new_msg_evnt_params["evnt_message_raw_text"] = evnt_message_text

    evnt_message_text = await get_attr_value_by_attr_chain(
        base_class_or_obj=event,
        attribute_chain="message.old_text")
    evnt_message_text = await clean_text(
        origin_text=evnt_message_text,
        clean_line_breaks=True,
        clean_continuous_spaces=True)
    new_msg_evnt_params["evnt_message_old_text"] = evnt_message_text

    evnt_message_raw_text = await get_attr_value_by_attr_chain(
        base_class_or_obj=event,
        attribute_chain="message.old_raw_text")
    evnt_message_text = await clean_text(origin_text=evnt_message_raw_text,
                                         clean_line_breaks=True,
                                         clean_continuous_spaces=True)
    new_msg_evnt_params["evnt_message_old_raw_text"] = evnt_message_text

    print(f"\nNEW MESSAGE EVENT:\n{'=' * 80}")
    for cur_param_str, cur_param_val in new_msg_evnt_params.items():
        if "empty_" in cur_param_str:
            print(f"\t")
            continue
        print(f"\t{cur_param_str} == {cur_param_val}")
    print(f"{'=' * 80}\n{'=' * 80}\n")
