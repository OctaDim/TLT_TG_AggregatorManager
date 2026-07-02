import unittest
from types import SimpleNamespace

from fastapi import HTTPException
from telethon import functions, types

from fast_api.app_telegram_folders_common.helper_telegram_folders_common import (
    build_dialog_filter,
    edit_archive_peers,
    get_next_folder_id,
    preview_folder_candidates,
    serialize_folder_filter,
)
from fast_api.app_telegram_folders_common.scheme_telegram_folders_common import (
    TGFolderDefinition,
    TGPeerRef,
)


class FakeTelegramClient:
    def __init__(self):
        self.user = types.User(
            id=101,
            first_name="Folder",
            last_name="User",
            username="folder_user",
            bot=False,
            contact=True)
        self.requests = []
        self.filters = []
        self.dialogs = []

    async def get_entity(self, entity):
        if entity in (101, "folder_user", self.user):
            return self.user
        if isinstance(entity, types.InputPeerUser) and entity.user_id == 101:
            return self.user
        raise ValueError("peer not found")

    async def get_input_entity(self, entity):
        if entity is self.user:
            return types.InputPeerUser(user_id=101, access_hash=999)
        raise ValueError("input peer not found")

    async def __call__(self, request):
        self.requests.append(request)
        if isinstance(request, functions.messages.GetDialogFiltersRequest):
            return self.filters
        return SimpleNamespace()

    def iter_dialogs(self, **kwargs):
        async def iterator():
            for dialog in self.dialogs:
                yield dialog
        return iterator()


class TelegramFoldersCommonTests(unittest.IsolatedAsyncioTestCase):
    async def test_build_dialog_filter_adds_pinned_peer_to_include_list(self):
        client = FakeTelegramClient()
        definition = TGFolderDefinition(
            title="Work",
            pinned_peers=[TGPeerRef(peer_id=101, peer_storage_type="user")])

        filter_obj = await build_dialog_filter(client, 2, definition)

        self.assertEqual(filter_obj.id, 2)
        self.assertEqual(filter_obj.title.text, "Work")
        self.assertEqual(filter_obj.pinned_peers[0].user_id, 101)
        self.assertEqual(filter_obj.include_peers[0].user_id, 101)

    async def test_build_dialog_filter_rejects_include_exclude_conflict(self):
        client = FakeTelegramClient()
        peer_ref = TGPeerRef(peer_id=101, peer_storage_type="user")
        definition = TGFolderDefinition(
            title="Work",
            include_peers=[peer_ref],
            exclude_peers=[peer_ref])

        with self.assertRaises(HTTPException) as context:
            await build_dialog_filter(client, 2, definition)

        self.assertEqual(context.exception.status_code, 400)

    async def test_archive_and_unarchive_use_server_folder_ids(self):
        client = FakeTelegramClient()
        peers = [TGPeerRef(peer_id=101, peer_storage_type="user")]

        await edit_archive_peers(client, peers, archived=True)
        await edit_archive_peers(client, peers, archived=False)

        self.assertEqual(client.requests[0].folder_peers[0].folder_id, 1)
        self.assertEqual(client.requests[1].folder_peers[0].folder_id, 0)

    async def test_explicit_include_overrides_dynamic_exclusions_in_preview(self):
        client = FakeTelegramClient()
        client.dialogs = [SimpleNamespace(
            entity=client.user,
            title="Folder User",
            archived=True,
            unread_count=0,
            dialog=SimpleNamespace(notify_settings=None))]
        definition = TGFolderDefinition(
            title="Work",
            include_peers=[TGPeerRef(peer_id=101)],
            exclude_archived=True,
            exclude_read=True)

        candidates = await preview_folder_candidates(client, definition, 10)

        self.assertTrue(candidates[0].included)
        self.assertEqual(candidates[0].reasons, ["explicitly_included"])

    async def test_next_folder_id_skips_existing_ids(self):
        client = FakeTelegramClient()
        client.filters = [
            types.DialogFilter(
                id=2,
                title=types.TextWithEntities(text="One", entities=[]),
                pinned_peers=[],
                include_peers=[],
                exclude_peers=[],
                contacts=True),
        ]

        self.assertEqual(await get_next_folder_id(client), 3)

    async def test_serialized_folder_contains_enriched_peer_data(self):
        client = FakeTelegramClient()
        input_peer = types.InputPeerUser(user_id=101, access_hash=999)
        filter_obj = types.DialogFilter(
            id=2,
            title=types.TextWithEntities(text="Work", entities=[]),
            pinned_peers=[input_peer],
            include_peers=[input_peer],
            exclude_peers=[],
            contacts=True)

        folder = await serialize_folder_filter(client, filter_obj)

        self.assertEqual(folder.title, "Work")
        self.assertEqual(folder.include_peers[0].first_name_cst, "Folder")
        self.assertEqual(folder.include_peers[0].peer_type_cst, "user")
        self.assertIsNone(folder.include_peers[0].bot_cst)


if __name__ == "__main__":
    unittest.main()
