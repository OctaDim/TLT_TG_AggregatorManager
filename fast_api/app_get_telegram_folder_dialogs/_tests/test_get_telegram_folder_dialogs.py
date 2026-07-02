import asyncio
import unittest
from datetime import datetime, timezone
from types import SimpleNamespace

from telethon import types

from fast_api.app_get_telegram_folder_dialogs.helper_get_telegram_folder_dialogs import (
    clear_dialogs_snapshot_cache,
    get_matching_folder_dialogs,
    schedule_dialogs_snapshot_warmup,
)


def create_dialog(entity_obj, message_id, archived=False,
                  unread_count=0, unread_mark=False):
    message_obj = SimpleNamespace(
        id=message_id,
        date=datetime(2026, 1, message_id, tzinfo=timezone.utc),
        message="Message %s" % (message_id,),
        raw_text="Message %s" % (message_id,),
        out=False)
    return SimpleNamespace(
        entity=entity_obj,
        title=getattr(entity_obj, "first_name", None) or
              getattr(entity_obj, "title", None),
        message=message_obj,
        date=message_obj.date,
        archived=archived,
        unread_count=unread_count,
        pinned=False,
        draft=None,
        dialog=SimpleNamespace(
            unread_mark=unread_mark,
            notify_settings=SimpleNamespace(mute_until=None)))


class FakeTelegramClient:
    def __init__(self, root_dialogs, archive_dialogs, iterator_delay=0):
        self.root_dialogs = root_dialogs
        self.archive_dialogs = archive_dialogs
        self.iterator_delay = iterator_delay
        self.requested_folder_ids = []

    def iter_dialogs(self, limit=None, folder=None):
        self.requested_folder_ids.append(folder)
        dialogs = self.archive_dialogs if folder == 1 else self.root_dialogs

        async def iterator():
            for dialog_obj in dialogs:
                if self.iterator_delay:
                    await asyncio.sleep(self.iterator_delay)
                yield dialog_obj
        return iterator()

    async def get_me(self):
        return self.root_dialogs[0].entity


def create_contact_filter():
    return types.DialogFilter(
        id=2,
        title=types.TextWithEntities(text="Folder", entities=[]),
        pinned_peers=[],
        include_peers=[],
        exclude_peers=[],
        contacts=True)


class GetTelegramFolderDialogsTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        clear_dialogs_snapshot_cache()

    def tearDown(self):
        clear_dialogs_snapshot_cache()

    async def test_filters_both_server_peer_folders_and_restores_pin_order(self):
        pinned_user = types.User(
            id=1, first_name="Pinned", contact=False, bot=False)
        explicit_archived_user = types.User(
            id=2, first_name="Explicit", contact=False, bot=False)
        unread_contact = types.User(
            id=3, first_name="Unread", contact=True, bot=False)
        excluded_contact = types.User(
            id=4, first_name="Excluded", contact=True, bot=False)
        read_contact = types.User(
            id=5, first_name="Read", contact=True, bot=False)
        archived_contact = types.User(
            id=6, first_name="Archived", contact=True, bot=False)

        client = FakeTelegramClient(
            root_dialogs=[
                create_dialog(unread_contact, 5, unread_count=1),
                create_dialog(excluded_contact, 6, unread_count=1),
                create_dialog(read_contact, 7),
                create_dialog(pinned_user, 1),
            ],
            archive_dialogs=[
                create_dialog(explicit_archived_user, 2, archived=True),
                create_dialog(archived_contact, 8, archived=True,
                              unread_count=1),
            ])
        filter_obj = types.DialogFilter(
            id=2,
            title=types.TextWithEntities(text="Folder", entities=[]),
            pinned_peers=[types.InputPeerUser(user_id=1, access_hash=11)],
            include_peers=[types.InputPeerUser(user_id=2, access_hash=22)],
            exclude_peers=[types.InputPeerUser(user_id=4, access_hash=44)],
            contacts=True,
            exclude_read=True,
            exclude_archived=True)

        dialogs, scanned_count, metrics = await get_matching_folder_dialogs(
            client, filter_obj, "config", dialogs_limit=100)

        self.assertEqual(client.requested_folder_ids, [0, 1])
        self.assertEqual(scanned_count, 6)
        self.assertEqual([item["peer_id"] for item in dialogs], [1, 3, 2])
        self.assertEqual(dialogs[0]["folder_match_reason"], "pinned")
        self.assertTrue(dialogs[0]["is_pinned"])
        self.assertEqual(
            dialogs[2]["folder_match_reason"], "explicitly_included")
        self.assertTrue(dialogs[2]["is_archived"])
        self.assertEqual(metrics["snapshot_source"], "telegram_refresh")
        self.assertGreaterEqual(metrics["snapshot_scan_ms"], 0)

    async def test_dialogs_limit_is_applied_after_membership_filtering(self):
        users = [types.User(
            id=index,
            first_name="User %s" % (index,),
            contact=True,
            bot=False) for index in range(1, 5)]
        client = FakeTelegramClient(
            root_dialogs=[create_dialog(user, index, unread_count=1)
                          for index, user in enumerate(users, start=1)],
            archive_dialogs=[])

        dialogs, scanned_count, _ = await get_matching_folder_dialogs(
            client, create_contact_filter(), "config", dialogs_limit=2)

        self.assertEqual(scanned_count, 4)
        self.assertEqual([item["peer_id"] for item in dialogs], [4, 3])

    async def test_reuses_snapshot_within_ttl(self):
        user = types.User(
            id=1, first_name="Cached", contact=True, bot=False)
        client = FakeTelegramClient(
            root_dialogs=[create_dialog(user, 1, unread_count=1)],
            archive_dialogs=[])

        _, _, first_metrics = await get_matching_folder_dialogs(
            client, create_contact_filter(), "config", dialogs_limit=10)
        _, _, second_metrics = await get_matching_folder_dialogs(
            client, create_contact_filter(), "config", dialogs_limit=10)

        self.assertEqual(client.requested_folder_ids, [0, 1])
        self.assertEqual(first_metrics["snapshot_source"], "telegram_refresh")
        self.assertEqual(second_metrics["snapshot_source"], "cache")
        self.assertEqual(second_metrics["snapshot_scan_ms"], 0)

    async def test_concurrent_requests_share_one_snapshot_scan(self):
        user = types.User(
            id=1, first_name="Concurrent", contact=True, bot=False)
        client = FakeTelegramClient(
            root_dialogs=[create_dialog(user, 1, unread_count=1)],
            archive_dialogs=[],
            iterator_delay=0.01)

        results = await asyncio.gather(
            get_matching_folder_dialogs(
                client, create_contact_filter(), "config", dialogs_limit=10),
            get_matching_folder_dialogs(
                client, create_contact_filter(), "config", dialogs_limit=10))

        self.assertEqual(client.requested_folder_ids, [0, 1])
        self.assertEqual(
            sorted(result[2]["snapshot_source"] for result in results),
            ["single_flight_cache", "telegram_refresh"])

    async def test_folder_list_warmup_primes_snapshot(self):
        user = types.User(
            id=1, first_name="Warm", contact=True, bot=False)
        client = FakeTelegramClient(
            root_dialogs=[create_dialog(user, 1, unread_count=1)],
            archive_dialogs=[],
            iterator_delay=0.01)

        self.assertTrue(schedule_dialogs_snapshot_warmup(client, "config"))
        _, _, metrics = await get_matching_folder_dialogs(
            client, create_contact_filter(), "config", dialogs_limit=10)

        self.assertEqual(client.requested_folder_ids, [0, 1])
        self.assertIn(metrics["snapshot_source"], (
            "cache", "single_flight_cache", "telegram_refresh"))
        self.assertEqual(client.requested_folder_ids.count(0), 1)
        self.assertEqual(client.requested_folder_ids.count(1), 1)


if __name__ == "__main__":
    unittest.main()
