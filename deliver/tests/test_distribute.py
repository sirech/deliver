# -*- coding: utf-8 -*-
from test_base import BaseTest, load_msg, get_msg
from mock import Mock

from deliver.distribute import Distributor
from deliver.read import Reader
from deliver.send import Sender

class DistributeTest(BaseTest):

    def setUp(self):
        super(DistributeTest,self).setUp()
        self.distributor = Distributor(self.config)
        self.sender = Mock(spec=Sender)
        self.distributor._sender = self.sender
        self.reader = Mock(spec=Reader)
        self.distributor._reader = self.reader
        self.msg = load_msg('sample')

    def _check_start_stop(self):
        self.reader.connect.assert_called_once_with()
        self.reader.new_messages.assert_called_once_with()
        self.reader.disconnect.assert_called_once_with()

    def _check_interactions(self, *ids):
        self.assertEqual(self.sender.send.call_count, len(ids))
        self.assertEqual(self.reader.delete.call_count, len(ids))
        self.assertEqual(tuple(id[0] for id, _ in self.reader.delete.call_args_list), ids)

    def _check_archived(self, *msgs):
        for msg in msgs:
            parsed_msg = get_msg(self.distributor._store, msg['Message-Id'])
            self.assertTrue(parsed_msg.received_at is not None)
            self.assertTrue(parsed_msg.sent_at is not None)

    def test_update_nothing_new(self):
        self.reader.new_messages.return_value = []
        self.distributor.update()

        self._check_start_stop()
        self._check_interactions()

    def test_update_one_message(self):
        self.reader.new_messages.return_value = [1237]
        self.reader.get.return_value = self.msg
        self.distributor.update()

        self._check_start_stop()
        self._check_interactions(1237)
        self._check_archived(self.msg)

    def test_update_multiple_messages(self):
        messages = {
            1237 : self.msg,
            1238 : load_msg('sample3'),
            1239 : load_msg('sample5')
            }
        self.reader.new_messages.return_value = messages.keys()
        self.reader.get.side_effect = lambda id : messages[id]
        self.distributor.update()

        self._check_start_stop()
        self._check_interactions(*messages.keys())
        self._check_archived(*messages.values())

    def test_update_invalid_message(self):
        self.reader.new_messages.return_value = [1237]
        self.reader.get.return_value = load_msg('sample7')
        self.distributor.update()

        self._check_start_stop()
        self._check_interactions()

    def test_update_whitelisted_message(self):
        self.reader.new_messages.return_value = [1237]
        msg = load_msg('sample8')
        self.reader.get.return_value = msg
        self.distributor.update()

        self._check_start_stop()
        self._check_interactions(1237)
        self._check_archived(msg)

    # Check internal methods to make sure things are working
    # smoothly

    def test_isvalid(self):
        self.assertTrue(self.distributor._isvalid(self.msg))

    def test_isvalid_whitelist(self):
        self.assertTrue(self.distributor._isvalid(load_msg('sample8')))

    def test_isvalid_false(self):
        self.assertFalse(self.distributor._isvalid(load_msg('sample7')))

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
        with_emails = load_msg('sample3')
        self.distributor._edit_msg(with_emails)
        texts = [msg.get_payload(decode=True) for msg in with_emails.get_payload()]
        for text in texts:
            self.assertTrue('sender@' in text)
            self.assertFalse('@host.com' in text)

    def test_create_header_special_chars(self):
        simple_sender = load_msg('sample2')
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
