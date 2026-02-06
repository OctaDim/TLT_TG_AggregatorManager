from dataclasses import dataclass


@dataclass(frozen=True)
class SQLADMIN_FILTERS:
    TELEGRAM_INVITES_URLS: tuple = (
        # https://t.me/joinchat/[unique_code]
        # https://t.me/+[unique_code]
        "https://t.me/joinchat/",
        "https://t.me/+", )

    WHATSAPP_INVITES_URLS: tuple = (
        # https://chat.whatsapp.com/[unique_code]
        "https://chat.whatsapp.com/", )

    DISCORD_INVITES_URLS: tuple = (
        # https://discord.gg/[unique_code]
        "https://discord.gg/", )

    VIBER_INVITES_URLS: tuple = (
        # https://invite.viber.com/?[parameters]
        "https://invite.viber.com/?", )

    SLACK_INVITES_URLS: tuple = (
        # https://[workspace].slack.com/join/[unique_code]
        ".slack.com/join/", )

    SIGNAL_INVITES_URLS: tuple = (
        # https://signal.group/#[encoded_data]
        "https://signal.group/#", )

    VK_INVITES_URLS: tuple = (
        # only personal, system level, not url
        # https://vk.com/club[ID_community]?invite=[unique_hash]
        # https://vk.com/[short_address]?invite=[unique_hash]
        # https://vk.com/video-[video_call_id]
        "https://vk.cc/",
        "https://vk.com/club",
        "?invite=",
        "https://vk.com/video-", )

    MAX_INVITES_URLS: tuple = (
        # https://max.ru/[unique_number]
        "https://max.ru/join/", )

    IMAGE_FILTER_EXTENSIONS: tuple = (
    "jpg", "jpeg", "png", "gif", "webp", "bmp", "ico", "svg", "tiff", "tif",
    "heic", "heif", "avif", "apng", "jfif", "pjpeg", "pjp", )

    IMAGE_FILTER_MIME_TYPES: tuple = (
    "image/jpeg", "image/jpg", "image/pjpeg", "image/jfif", "image/png",
    "image/x-png", "image/apng", "image/gif", "image/webp", "image/bmp",
    "image/x-bmp", "image/x-ms-bmp", "image/x-icon", "image/vnd.microsoft.icon",
    "image/svg+xml", "image/svg", "image/tiff", "image/tif", "image/tiff-fx",
    "image/heic", "image/heif", "image/heic-sequence", "image/heif-sequence",
    "image/avif", "image/x-portable-bitmap", "image/x-portable-graymap",
    "image/x-portable-pixmap", "image/x-xcf", "image/x-raw", )

    AUDIO_FILTER_EXTENSIONS: tuple = (
        "mp3", "mpga", "mpeg", "wav", "wave", "m4a", "aac", "flac",
        "ogg",)
    AUDIO_FILTER_MIME_TYPES: tuple = (
        "audio/mpeg", "audio/wav", "audio/x-wav", "audio/wave",
        "audio/mp4", "audio/x-m4a", "audio/m4a", "audio/aac",
        "audio/x-aac", "audio/flac", "audio/x-flac", "audio/ogg",
        "application/ogg", "audio/3gpp",)

    VIDEO_FILTER_EXTENSIONS: tuple = (
        "mp4", "m4v", "avi", "mkv", "webm", "mov", "qt", "wmv", "flv",
        "ogv", "3gp", "3g2", "mpeg", "mpg", "ts ", "mts", "m2ts", "mxf",
        "divx", "f4v", "vob", "asf", "rm", "rmvb", "swf", "heic", "heif",)
    VIDEO_FILTER_MIME_TYPES: tuple = (
        "video/mp4", "application/mp4", "video/x-m4v", "video/mp4",
        "video/x-msvideo", "video/avi", "video/msvideo", "video/x-matroska",
        "video/webm", "video/quicktime", "video/x-quicktime",
        "video/x-ms-wmv", "video/x-flv", "application/x-shockwave-flash",
        "video/ogg", "application/ogg", "video/ogm", "video/3gpp",
        "video/3gp", "audio/3gpp", "video/3gpp2", "video/mpeg",
        "video/mp2t", "video/MP2T", "application/mxf", "video/mxf",
        "video/divx", "video/x-msvideo",)

    EMOJI_FILTER_EXTENSIONS: tuple = ("webp", )
    EMOJI_FILTER_MIME_TYPES: tuple = ("image/webp", )

    DOCS_FILTER_EXTENSIONS: tuple = (
    "doc", "docx", "dot", "dotx", "docm", "dotm",
    "xls", "xlsx", "xlt", "xltx", "xlsm", "xltm",
    "ppt", "pptx", "pps", "ppsx", "pot", "potx",
    "odt", "ott", "oth", "odm", "ods", "ots", "odp", "otp", "odg", "otg",
    "pdf", "epub", "mobi", "azw", "azw3", "ibooks",
    "txt", "rtf", "md", "markdown", "tex", "log",
    "csv", "tsv", "xml", "html", "htm", "xhtml", "json", )
    DOCS_FILTER_MIME_TYPES: tuple = (
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.template",
    "application/vnd.ms-word.document.macroEnabled.12",
    "application/vnd.ms-word.template.macroEnabled.12",
    "application/vnd.ms-excel",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.template",
    "application/vnd.ms-excel.sheet.macroEnabled.12",
    "application/vnd.ms-excel.template.macroEnabled.12",
    "application/vnd.ms-powerpoint",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    "application/vnd.openxmlformats-officedocument.presentationml.template",
    "application/vnd.openxmlformats-officedocument.presentationml.slideshow",
    "application/vnd.oasis.opendocument.text",
    "application/vnd.oasis.opendocument.text-template",
    "application/vnd.oasis.opendocument.spreadsheet",
    "application/vnd.oasis.opendocument.spreadsheet-template",
    "application/vnd.oasis.opendocument.presentation",
    "application/vnd.oasis.opendocument.presentation-template",
    "application/vnd.oasis.opendocument.graphics",
    "application/vnd.oasis.opendocument.graphics-template",
    "application/pdf", "application/epub+zip",
    "application/x-mobipocket-ebook", "application/vnd.amazon.ebook",
    "text/plain", "text/richtext", "application/rtf", "text/markdown",
    "text/x-tex", "text/csv", "text/tab-separated-values",
    "application/xml", "text/html", "text/htm", "application/xhtml+xml",
    "application/json", "text/json", )
