import os
import email

from datetime import datetime
from sqlalchemy.exc import IntegrityError

from deliver.tests.test_base import BaseTest, load_msg, load_all_msg
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

    def tearDown(self):
        super(SQLiteTest,self).tearDown()
        os.remove(self.db_cfg['name'])

    def test_write_very_simple_msg(self):
        self.db.messages.insert().values(content='a message', received_at=datetime.now()).execute()

    def _write_msgs(self):
        mails = load_all_msg()
        for mail in mails:
            self.db.messages.insert().values(content=mail.as_string(),
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
        mail = email.message_from_string(self.db.messages.
                                         select(self.db.messages.c.id == 1).execute()
                                         .fetchone()['content'])
        # import difflib
        # import sys
        # base = load_msg('sample')
        # print base.as_string().split('\n')
        # print '#' * 60
        # print mail.as_string().split('\n')

    def test_write_valid_digest(self):
        self.db.digests.insert().values(msg_id=1,
                                        send_to='test@mail.com',
                                        scheduled_at=datetime.now()).execute()

