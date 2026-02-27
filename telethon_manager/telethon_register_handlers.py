import weakref

from telethon import events

from telethon_manager.telethon_handlers.hdr_helper_album_event import (
    album_event_handler_helper)
from telethon_manager.telethon_handlers.hdr_helper_callback_query import (
    callback_query_handler_helper)
from telethon_manager.telethon_handlers.hdr_helper_chat_action import (
    chat_action_handler_helper)
from telethon_manager.telethon_handlers.hdr_helper_inline_query import (
    inline_query_handler_helper)
from telethon_manager.telethon_handlers.hdr_helper_message_deleted import (
    message_deleted_handler_helper)
from telethon_manager.telethon_handlers.hdr_helper_message_edited import (
    message_edited_handler_helper)
from telethon_manager.telethon_handlers.hdr_helper_message_read import (
    message_read_handler_helper)
from telethon_manager.telethon_handlers.hdr_helper_new_message import (
    new_message_handler_helper)
from telethon_manager.telethon_handlers.hdr_helper_raw_event import (
    raw_event_handler_helper)
from telethon_manager.telethon_handlers.hdr_helper_user_update import (
    user_update_handler_helper)


async def add_all_telethon_client_handlers(
        telethon_manager: "TelethonManagerSingleton",
        # telethon_client: TelegramClient,
        # telethon_config: TelethonConfig,
        telethon_client_weak_ref: weakref.ref,
        telethon_config_weak_ref: weakref.ref,
) -> None:
    # TODO: Think if weak_ref necessary
    telethon_client = telethon_client_weak_ref()
    telethon_config = telethon_config_weak_ref()

    config_name = telethon_config.name
    cur_client_handlers = []

    # NewMessage Handler
    @telethon_client.on(events.NewMessage())
    async def new_message_handler(event):
        await new_message_handler_helper(
            event=event,
            telethon_client=telethon_client,
            telethon_config=telethon_config,
            event_type="NewMessage")

    cur_client_handlers.append(new_message_handler)

    # MessageEdited Handler
    @telethon_client.on(events.MessageEdited())
    async def message_edited_handler(event):
        await message_edited_handler_helper(
            event=event,
            telethon_client=telethon_client,
            telethon_config=telethon_config,
            event_type="MessageEdited")

    cur_client_handlers.append(message_edited_handler)

    # MessageRead Handler
    @telethon_client.on(events.MessageRead())
    async def message_read_handler(event):
        await message_read_handler_helper(
            event=event,
            telethon_client=telethon_client,
            telethon_config=telethon_config,
            event_type="MessageRead")

    cur_client_handlers.append(message_read_handler)

    # MessageDeleted Handler
    @telethon_client.on(events.MessageDeleted())
    async def message_deleted_handler(event):
        await message_deleted_handler_helper(
            event=event,
            telethon_client=telethon_client,
            telethon_config=telethon_config,
            event_type="MessageDeleted")

    cur_client_handlers.append(message_deleted_handler)

    # ChatAction Handler
    @telethon_client.on(events.ChatAction())
    async def chat_action_handler(event):
        await chat_action_handler_helper(
            event=event,
            telethon_client=telethon_client,
            telethon_config=telethon_config,
            event_type="ChatAction")

    cur_client_handlers.append(chat_action_handler)

    # UserUpdate Handler
    @telethon_client.on(events.UserUpdate())
    async def user_update_handler(event):
        await user_update_handler_helper(
            event=event,
            telethon_client=telethon_client,
            telethon_config=telethon_config,
            event_type="UserUpdate")

    cur_client_handlers.append(user_update_handler)

    # CallbackQuery Handler
    @telethon_client.on(events.CallbackQuery())
    async def callback_query_handler(event):
        await callback_query_handler_helper(
            event=event,
            telethon_client=telethon_client,
            telethon_config=telethon_config,
            event_type="CallbackQuery")

    cur_client_handlers.append(callback_query_handler)

    # InlineQuery Handler
    @telethon_client.on(events.InlineQuery())
    async def inline_query_handler(event):
        await inline_query_handler_helper(
            event=event,
            telethon_client=telethon_client,
            telethon_config=telethon_config,
            event_type="InlineQuery")

    cur_client_handlers.append(inline_query_handler)

    # Raw Handler
    @telethon_client.on(events.Raw())
    async def raw_event_handler(event):
        await raw_event_handler_helper(
            event=event,
            telethon_client=telethon_client,
            telethon_config=telethon_config,
            event_type="Raw")

    cur_client_handlers.append(raw_event_handler)

    # Album Handler
    @telethon_client.on(events.Album())
    async def album_event_handler(event):
        await album_event_handler_helper(
            event=event,
            telethon_client=telethon_client,
            telethon_config=telethon_config,
            event_type="Album")

    cur_client_handlers.append(album_event_handler)

    # Saving all weak ref handlers
    telethon_manager.event_handlers[config_name] = cur_client_handlers
