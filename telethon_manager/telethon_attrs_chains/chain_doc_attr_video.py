def get_doc_attr_video_attr_chains():
    attrs_chains = {
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
        # document_attribute_file_name
        "document_attribute_file_name": {
            "doc_attr_file_name": "file_name",  # XXX
            "separator": ""},
    }
    return attrs_chains
