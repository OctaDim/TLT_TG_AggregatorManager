def get_client_sent_msg_text_attr_chains():
    attrs_chains = {
        # Getting from Message object, not from Event object
        "message": {
            "ev_message_message": "message",
            "separator": ""},
        "message_text": {
            "ev_message_text": "text",
            "separator": ""},
        "message_raw_text": {
            "ev_message_raw_text": "raw_text",
            f"separator": ""},
    }
    return attrs_chains
