def get_user_data_attr_chains():
    attrs_chains = {
        # user (User)
        "user": {
            "user_id": "id",
            "user_is_self": "is_self",
            "user_contact": "contact",
            "user_mutual_contact": "mutual_contact",
            "user_deleted": "deleted",
            "user_bot": "bot",
            "user_bot_chat_history": "bot_chat_history",
            "user_bot_nochats": "bot_nochats",
            "user_verified": "verified",
            "user_restricted": "restricted",
            "user_min": "min",
            "user_bot_inline_geo": "bot_inline_geo",
            "user_support": "support",
            "user_scam": "scam",
            "user_apply_min_photo": "apply_min_photo",
            "user_fake": "fake",
            "user_bot_attach_menu": "bot_attach_menu",
            "user_premium": "premium",
            "user_attach_menu_enabled": "attach_menu_enabled",
            "user_bot_can_edit": "bot_can_edit",
            "user_close_friend": "close_friend",
            "user_stories_hidden": "stories_hidden",
            "user_stories_unavailable": "stories_unavailable",
            "user_contact_require_premium": "contact_require_premium",
            "user_bot_business": "bot_business",
            "user_bot_has_main_app": "bot_has_main_app",
            "user_bot_forum_view": "bot_forum_view",
            "user_access_hash": "access_hash",
            "user_first_name": "first_name",
            "user_last_name": "last_name",
            "user_username": "username",
            "user_phone": "phone",
            "user_photo": "photo",
            "user_status": "status",
            "user_bot_info_version": "bot_info_version",
            "user_restriction_reason": "restriction_reason",  # List[RestrictionReason]
            "user_bot_inline_placeholder": "bot_inline_placeholder",
            "user_lang_code": "lang_code",
            "user_emoji_status": "emoji_status",  # (EmojiStatus)
            "user_usernames": "usernames",  # List[Username]
            "user_stories_max_id": "stories_max_id",
            "user_color": "color",  # (PeerColor)
            "user_profile_color": "profile_color",  # (PeerColor)
            "user_bot_active_users": "bot_active_users",
            "user_bot_verification_icon": "bot_verification_icon",
            "user_send_paid_messages_stars": "send_paid_messages_stars",
            "separator": ""},
    }
    return attrs_chains
