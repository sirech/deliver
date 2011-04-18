from datetime import datetime

from deliver.tests.test_base import BaseTest, load_msg, get_msg
from deliver.db.store import Store

class StoreTest(BaseTest):

    def setUp(self):
        super(StoreTest,self).setUp()
        self.store = Store(self.config)

    def _get_msg(self, id):
        return get_msg(self.store, id)

    def _store_msg(self, fileName):
        msg = load_msg('sample')
        self.store.archive(msg)
        return msg

    def test_archive(self):
        msg = load_msg('sample')
        self.assertEqual(self.store.archive(msg), msg['Message-Id'])
        self.assertEqual(self._get_msg(msg['Message-Id']).content, msg.as_string())

    def test_archive_msg(self):
        msg = self._store_msg('sample')
        parsed_msg = self._get_msg(msg['Message-Id']).parsed_content
        self.assertEqual(parsed_msg['Subject'], u'BETA 2.0')
        self.assertEqual(parsed_msg['To'], u'sender@host.com')

    def _date_is_today(self, d):
        self.assertEqual(d.date(), datetime.now().date())

    def test_archive_date(self):
        msg = self._store_msg('sample')
        parsed_msg = self._get_msg(msg['Message-Id'])
        self.assertTrue(parsed_msg.sent_at is None)
        self._date_is_today(parsed_msg.received_at)

    def test_mark_as_sent(self):
        msg = self._store_msg('sample')
        self.store.mark_as_sent(msg['Message-Id'])
        parsed_msg = self._get_msg(msg['Message-Id'])
        self._date_is_today(parsed_msg.sent_at)
