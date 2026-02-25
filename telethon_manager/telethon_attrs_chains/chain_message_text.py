def get_message_text_attr_chains():
    attrs_chains = {
        # reaction_result
        "message_message": {
            "ev_message_message": "message.message",
            "separator": ""},
        "message_text": {
            "ev_message_text": "message.text",
            "separator": ""},
        "message_raw_text": {
            "ev_message_raw_text": "message.raw_text",
            f"separator": ""},
    }
    return attrs_chains
