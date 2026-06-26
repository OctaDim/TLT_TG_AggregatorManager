import unittest

from utils_specific.enrich_sender_profile_data import enrich_sender_profile_data


class FakeUsername:
    def __init__(self, username, active=True):
        self.username = username
        self.active = active


class FakeSender:
    def __init__(self, username=None, first_name=None, last_name=None, phone=None, bot=None, usernames=None):
        self.username = username
        self.first_name = first_name
        self.last_name = last_name
        self.phone = phone
        self.bot = bot
        self.usernames = usernames or []


class FakeEvent:
    def __init__(self, sender=None, sender_id=None, sender_exc=None, fetched_sender=None):
        self.sender = sender
        self.sender_id = sender_id
        self._sender_exc = sender_exc
        self._fetched_sender = fetched_sender
        self.get_sender_calls = 0

    async def get_sender(self):
        self.get_sender_calls += 1
        if self._sender_exc:
            raise self._sender_exc
        return self._fetched_sender


class FakeClient:
    def __init__(self, entity=None):
        self.entity = entity
        self.calls = []

    async def get_entity(self, entity):
        self.calls.append(entity)
        return self.entity


class EnrichSenderProfileDataTests(unittest.IsolatedAsyncioTestCase):
    async def test_skips_fetch_when_all_sender_fields_are_present(self):
        event = FakeEvent(fetched_sender=FakeSender(username='new_username'))
        event_params = {
            'tlt_sender_username': 'existing_username',
            'tlt_sender_first_name': 'Existing',
            'tlt_sender_last_name': 'User',
            'tlt_sender_phone': '+10000000000',
            'tlt_sender_bot': False,
        }

        result = await enrich_sender_profile_data(
            event=event,
            telethon_client=None,
            event_params=event_params,
        )

        self.assertEqual(result, {})
        self.assertEqual(event.get_sender_calls, 0)

    async def test_enriches_from_event_get_sender_with_collectible_username_fallback(self):
        sender = FakeSender(
            username=None,
            first_name='Alice',
            last_name='Walker',
            phone=None,
            bot=False,
            usernames=[FakeUsername('alice_collectible', active=True)],
        )
        event = FakeEvent(fetched_sender=sender)

        result = await enrich_sender_profile_data(
            event=event,
            telethon_client=None,
            event_params={'tlt_sender_username': None, 'tlt_sender_first_name': '', 'tlt_sender_last_name': None, 'tlt_sender_phone': None, 'tlt_sender_bot': None},
        )

        self.assertEqual(result['tlt_sender_username'], 'alice_collectible')
        self.assertEqual(result['tlt_sender_first_name'], 'Alice')
        self.assertEqual(result['tlt_sender_last_name'], 'Walker')
        self.assertFalse(result['tlt_sender_bot'])
        self.assertEqual(event.get_sender_calls, 1)
        self.assertNotIn('tlt_sender_phone', result)

    async def test_uses_get_entity_to_fill_fields_still_missing_after_get_sender(self):
        fetched_sender = FakeSender(username='from_event', first_name='Eve', last_name=None, phone=None, bot=False)
        entity_sender = FakeSender(username='from_entity', first_name='Eve', last_name='Johnson', phone='+12223334444', bot=False)
        event = FakeEvent(fetched_sender=fetched_sender, sender_id=77)
        client = FakeClient(entity=entity_sender)

        result = await enrich_sender_profile_data(
            event=event,
            telethon_client=client,
            event_params={'tlt_sender_username': None, 'tlt_sender_first_name': None, 'tlt_sender_last_name': None, 'tlt_sender_phone': None, 'tlt_sender_bot': None},
        )

        self.assertEqual(client.calls, [77])
        self.assertEqual(result['tlt_sender_username'], 'from_event')
        self.assertEqual(result['tlt_sender_first_name'], 'Eve')
        self.assertEqual(result['tlt_sender_last_name'], 'Johnson')
        self.assertEqual(result['tlt_sender_phone'], '+12223334444')

    async def test_falls_back_to_client_get_entity_when_get_sender_fails(self):
        entity_sender = FakeSender(
            username='resolved_user',
            first_name='Bob',
            last_name='Stone',
            phone='+19998887766',
            bot=False,
        )
        event = FakeEvent(sender=None, sender_id=42, sender_exc=RuntimeError('boom'))
        client = FakeClient(entity=entity_sender)

        result = await enrich_sender_profile_data(
            event=event,
            telethon_client=client,
            event_params={'tlt_sender_username': None, 'tlt_sender_first_name': None, 'tlt_sender_last_name': None, 'tlt_sender_phone': None, 'tlt_sender_bot': None},
        )

        self.assertEqual(client.calls, [42])
        self.assertEqual(result, {
            'tlt_sender_username': 'resolved_user',
            'tlt_sender_first_name': 'Bob',
            'tlt_sender_last_name': 'Stone',
            'tlt_sender_phone': '+19998887766',
            'tlt_sender_bot': False,
        })


if __name__ == '__main__':
    unittest.main()
