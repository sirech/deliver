# -*- coding: utf-8 -*-
from test_base import BaseTest, load_msg, load_all_msg
from email.header import decode_header

from deliver.converter import UnicodeMessage

def convert_all(lst):
    return [UnicodeMessage(msg) for msg in lst]

class ConverterTest(BaseTest):

    def setUp(self):
        super(ConverterTest,self).setUp()
        self.msg = UnicodeMessage(load_msg('sample3'))

    def test_payload_encoding(self):
        for msg in convert_all(load_all_msg()):
            self._test_payload_encoding(msg)

    def _test_payload_encoding(self, msg):
        for part in msg.walk():
            self.assertTrue(part.get_content_maintype() != 'text'
                            or part.get_content_charset() == 'utf-8')

    def test_header_encoding(self):
        for msg in convert_all(load_all_msg()):
            self._test_header_encoding(msg)

    def _test_header_encoding(self, msg):
        for header in msg.values():
            for value, encoding in decode_header(header):
                self.assertTrue(encoding is None or encoding == 'utf-8')
                # should not raise exception
                unicode(value, encoding if encoding is not None else 'ascii')

    def test_get(self):
        self.assertEqual(self.msg['To'], u'sender@host.com')

    def test_get_special_chars(self):
        self.assertEqual(self.msg['Subject'], u'Re: [Test] atensión: los 10 curros mejor pagados!')

    def test_get_nokey(self):
        self.assertEqual(self.msg['Heathen'], None)

    def test_replace_header_ascii(self):
        s = u'Memorias de Adriano'
        self.msg.replace_header('Subject', s)
        self.assertEqual(self.msg['Subject'], s)
        self.assertEqual(self.msg._msg['Subject'], s.encode('ascii'))

    def test_replace_header_special_chars(self):
        s = u'Un día de cólera'
        self.msg.replace_header('Subject', s)
        self.assertEqual(self.msg['Subject'], s)
        self.assertEqual(self.msg._msg['Subject'], '=?utf-8?q?Un_d=C3=ADa_de_c=C3=B3lera?=')

    def test_set_payload(self):
        s = u'Con cien cañones por banda, viento en popa a toda vela'
        self.msg = UnicodeMessage(load_msg('sample'))
        self.msg.get_payload(0).set_payload(s)
        self.assertEqual(self.msg.get_payload(0).get_payload(),
                         'Con cien ca=C3=B1ones por banda, viento en popa a toda vela')

    def test_get_payload_decoded(self):
        self.msg = UnicodeMessage(load_msg('sample'))
        print self.msg.get_payload(0).get_payload().split('\n')

