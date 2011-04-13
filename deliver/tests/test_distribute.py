# -*- coding: utf-8 -*-
import email

from test_base import BaseTest
from mock import Mock

from deliver.distribute import Distributor
from deliver.read import Reader
from deliver.send import Sender

class DistributorTest(BaseTest):

    def setUp(self):
        super(DistributorTest,self).setUp()
        self.distributor = Distributor(self.config)
        self.sender = Mock(spec=Sender)
        self.distributor._sender = self.sender
        self.reader = Mock(spec=Reader)
        self.distributor._reader = self.reader
        self.msg = email.message_from_file(open('test_data/sample'))

    def test_update_nothing_new(self):
        self.reader.new_messages.return_value = []
        self.distributor.update()

        self._check_start_stop()

    def test_update_one_message(self):
        self.reader.new_messages.return_value = [1237]
        self.reader.get.return_value = self.msg
        self.distributor.update()

        self._check_start_stop()
        self.assertEqual(self.sender.send.call_count, 1)
        self.reader.delete.assert_called_once_with(1237)

    def _check_start_stop(self):
        self.reader.connect.assert_called_once_with()
        self.reader.new_messages.assert_called_once_with()
        self.reader.disconnect.assert_called_once_with()


    # Check internal methods to make sure things are working
    # smoothly

    def test_isvalid(self):
        self.assertTrue(self.distributor._isvalid(self.msg))

    def test_find_sender_email(self):
        self.assertEqual(self.distributor._find_sender_email(self.msg),
                         'test@mail.com')

    def test_find_actual_text(self):
        self.assertEqual(len(list((self.distributor._find_actual_text(self.msg)))),
                         2)

    def test_choose_intro(self):
        self.assertTrue(self.distributor._choose_intro() in self.config['introductions'])

    def test_create_footer(self):
        self.assertTrue(self.distributor._create_footer(self.msg)[2] in
                        self.config['quotes'])

    def test_edit_msg_anonymize(self):
        with_emails = email.message_from_file(open('test_data/sample3'))
        self.distributor._edit_msg(with_emails)
        texts = [msg.get_payload() for msg in with_emails.get_payload()]
        for text in texts:
            self.assertTrue('sender@' in text)
            self.assertFalse('@host.com' in text)

    def test_create_header_special_chars(self):
        simple_sender = email.message_from_file(open('test_data/sample2'))
        self.config['introductions'] = [ u'salté' ]
        self.assertEqual(self.distributor._create_header(simple_sender),
                         [u'MIA salté:'])

    def test_create_footer_special_chars(self):
        quote = u'salté la fuente'
        self.config['quotes'] = [quote]
        self.assertTrue(quote in self.distributor._create_footer(self.msg))

    def test_edit_msg_special_chars(self):
        self.config['introductions'] = [ u'salté' ]
        quote = u'salté la fuente'
        self.config['quotes'] = [quote]
        self.distributor._edit_msg(self.msg)
