def get_tg_msg_file_mime_type():
    attrs_chains = {
        # file mime type
        "file_mime_type": {
            "msg_file_mime_type": "file.mime_type",
            "separator": ""},
        # media mime type
        "media_mime_type": {
            "msg_media_mime_type": "media.mime_type",
            "separator": ""},
        # media file mime type
        "media_file_mime_type": {
            "msg_media_file_mime_type": "media.file.mime_type",
            "separator": ""},
        # media document mime type
        "media_document_mime_type": {
            "msg_media_doc_mime_type": "media.document.mime_type",
            f"separator": ""},
    }
    return attrs_chains
