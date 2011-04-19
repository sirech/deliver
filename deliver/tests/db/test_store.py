from datetime import datetime
from sqlalchemy.exc import IntegrityError

from deliver.tests.test_base import BaseTest, load_msg, get_msg, get_digests
from deliver.db.store import Store

class StoreTest(BaseTest):

    def setUp(self):
        super(StoreTest,self).setUp()
        self.store = Store(self.config)

    def _get_msg(self, id):
        return get_msg(self.store, id)

    def _store_msg(self, fileName):
        msg = load_msg(fileName)
        self.store.archive(msg)
        return (msg['Message-Id'], msg)

    def test_archive(self):
        msg = load_msg('sample')
        self.assertEqual(self.store.archive(msg), msg['Message-Id'])
        self.assertEqual(self._get_msg(msg['Message-Id']).content, msg.as_string())

    def test_archive_msg(self):
        id, msg = self._store_msg('sample')
        parsed_msg = self._get_msg(id).parsed_content
        self.assertEqual(parsed_msg['Subject'], u'BETA 2.0')
        self.assertEqual(parsed_msg['To'], u'sender@host.com')

    def _date_is_today(self, *dates):
        today = datetime.now().date()
        for d in dates:
            self.assertEqual(d.date(), today)

    def test_archive_date(self):
        id, msg = self._store_msg('sample')
        parsed_msg = self._get_msg(id)
        self.assertTrue(parsed_msg.sent_at is None)
        self._date_is_today(parsed_msg.received_at)

    def test_mark_as_sent(self):
        id, msg = self._store_msg('sample')
        self.store.mark_as_sent(id)
        parsed_msg = self._get_msg(id)
        self._date_is_today(parsed_msg.sent_at)

    def test_digest_no_msg(self):
        msg = load_msg('sample')
        # for some reason the assert is not working
        try:
            self.assertRaises(IntegrityError,
                              self.store.digest(msg['Message-Id'], u'test@mail.com'))
        except IntegrityError:
            return
        self.fail()

    def _digest_msg(self, fileName, *addresses):
        id, msg = self._store_msg(fileName)
        self.store.digest(id, *addresses)
        return (id, msg)

    def test_digest(self):
        id, msg = self._digest_msg('sample', u'test@mail.com')
        parsed_msg = self._get_msg(id)
        self.assertEqual(len(parsed_msg.digests), 1)
        digest = parsed_msg.digests[0]
        self.assertEqual(digest.send_to, u'test@mail.com')
        self.assertEqual(digest.msg_id, id)
        self.assertTrue(digest.sent_at is None)
        self.assertEqual(digest.msg.content, msg.as_string())

    def test_digest_multiple(self):
        addresses = [u'external@mail.com', u'test@mail.com']
        id, msg = self._digest_msg('sample', *addresses)
        self._store_msg('sample2')
        parsed_msg = self._get_msg(id)
        self.assertEqual([d.send_to for d in parsed_msg.digests], addresses)

    def test_users_with_pending_digests_empty(self):
        self.assertEqual(self.store.users_with_pending_digests(), set())

    def _digest_msgs(self, fileList, *addresses):
        return [self._digest_msg(f, *addresses) for f in fileList]

    def test_users_with_pending_digests(self):
        '''
        Generate digests for 3 users. Mark as read for first and
        last. Add more digests for first user. Users 1 and 2 should
        have pending digests.
        '''
        addresses = [u'external@mail.com', u'test@mail.com', u'another@mail.com']
        self._digest_msgs(['sample', 'sample2'], *addresses)
        self.store.mark_digest_as_sent(addresses[0])
        self.store.mark_digest_as_sent(addresses[2])
        self._digest_msgs(['sample3', 'sample4'], addresses[0])
        self.assertEqual(self.store.users_with_pending_digests(), set(addresses[0:2]))

    def test_mark_digest_as_sent_empty(self):
        self.assertEqual(self.store.mark_digest_as_sent(u'test@mail.com'), [])

    def test_mark_digest_as_sent(self):
        addresses = [u'external@mail.com', u'test@mail.com']
        msgs = self._digest_msgs(['sample', 'sample2'], *addresses)
        self.assertEqual(self.store.mark_digest_as_sent(addresses[0]),
                         [id for id, _ in msgs])
        self._date_is_today(*[d.sent_at for d in get_digests(self.store, addresses[0])])
        for digest in get_digests(self.store, addresses[1]):
            self.assertTrue(digest.sent_at is None)

