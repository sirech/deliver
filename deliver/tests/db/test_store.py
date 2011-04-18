from datetime import datetime

from deliver.tests.test_base import BaseTest, load_msg
from deliver.db.models import message
from deliver.db.store import Store

class StoreTest(BaseTest):

    def setUp(self):
        super(StoreTest,self).setUp()
        self.store = Store(self.config)

    def _get_msg(self, id):
        return self.store._db.session.query(message.Message).get(id)

    def test_archive(self):
        msg = load_msg('sample')
        self.assertEqual(self.store.archive(msg), msg['Message-Id'])
        self.assertEqual(self._get_msg(msg['Message-Id']).content, msg.as_string())

    def test_archive_msg(self):
        msg = load_msg('sample')
        self.store.archive(msg)
        parsed_msg = self._get_msg(msg['Message-Id']).parsed_content
        self.assertEqual(parsed_msg['Subject'], u'BETA 2.0')
        self.assertEqual(parsed_msg['To'], u'sender@host.com')

    def test_archive_date(self):
        msg = load_msg('sample')
        self.store.archive(msg)
        parsed_msg = self._get_msg(msg['Message-Id'])
        self.assertTrue(parsed_msg.sent_at is None)
        self.assertEqual(parsed_msg.received_at.date(), datetime.now().date())
