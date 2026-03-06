def get_doc_attr_audio_attr_chains():
    attrs_chains = {
        # document_attribute_audio
        "document_attribute_audio": {
            "doc_attr_duration": "duration",
            "doc_attr_voice": "voice",
            "doc_attr_title": "title",
            "doc_attr_performer": "performer",
            "doc_attr_waveform": "waveform",
            "separator": ""},
        # document_attribute_video
        "document_attribute_video": {
            "doc_attr_w": "w",
            "doc_attr_h": "h",
            "doc_attr_round_message": "round_message",
            "doc_attr_supports_streaming": "supports_streaming",
            "doc_attr_nosound": "nosound",
            "doc_attr_preload_prefix_size": "preload_prefix_size",
            "doc_attr_video_start_ts": "video_start_ts",
            "doc_attr_video_codec": "video_codec",
            "separator": ""},
    }
    return attrs_chains
