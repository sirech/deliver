import email

from datetime import datetime
from sqlalchemy.exc import IntegrityError

from deliver.tests.test_base import BaseTest, load_all_msg

from deliver.converter.simple import UnicodeMessage
from deliver.db.sqlite import DBWrapper

class SQLiteTest(BaseTest):
    '''
    This class test the basic process of connecting to sqlite,
    creating tables and manipulating data, without higher level
    models.
    '''
    def setUp(self):
        super(SQLiteTest,self).setUp()
        self.db_cfg = { 'name' : self.config['db_name'] }
        self.db = DBWrapper(**self.db_cfg)

    def _write_stub_msg(self):
        self.db.messages.insert().values(id='123',
                                         content='a message', received_at=datetime.now()).execute()

    def test_write_very_simple_msg(self):
        self._write_stub_msg()

    def _write_msgs(self):
        mails = load_all_msg()
        for mail in mails:
            self.db.messages.insert().values(
                id=mail['Message-Id'],
                content=mail.as_string(),
                received_at=datetime.now()).execute()

    def test_write_valid_msg(self):
        self._write_msgs()

    def test_write_invalid_no_msg(self):
        self.assertRaises(IntegrityError,
                          self.db.messages.insert().values(received_at=datetime.now()).execute)

    def test_write_invalid_no_received(self):
        self.assertRaises(IntegrityError,
                          self.db.messages.insert().values(content='a message',
                                                           sent_at=datetime.now()).execute)

    def test_read_valid_msg(self):
        self._write_msgs()
        mail = UnicodeMessage(email.message_from_string(self.db.messages.select().execute()
                                                        .fetchone()['content'].encode('utf-8')))

        self.assertEqual(mail['Subject'], u'BETA 2.0')
        self.assertEqual(mail['To'], u'sender@host.com')
        self.assertEqual(mail['From'], u'Name<test@mail.com>')

    def test_write_valid_digest(self):
        self._write_stub_msg()
        self.db.digests.insert().values(msg_id='123',
                                        send_to=u'test@mail.com',
                                        scheduled_at=datetime.now()).execute()

