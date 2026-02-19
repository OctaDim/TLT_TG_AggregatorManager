def get_msg_delete_attr_chains():
    attrs_chains = {
        # MessageDeleted
        "delete_message": {
            "original_update_messages": "original_update.messages",
            "original_update_pts": "original_update.pts",
            "original_update_pts_count": "original_update.pts_count",
            "event_deleted_id": "deleted_id",
            "event_deleted_ids": "deleted_ids",
            "separator": "", },
    }
    return attrs_chains
