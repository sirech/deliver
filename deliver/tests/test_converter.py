# -*- coding: utf-8 -*-
from test_base import BaseTest, load_msg

class ConverterTest(BaseTest):

    def setUp(self):
        super(ConverterTest,self).setUp()
        self.msg = load_msg('sample3')

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
        self.msg = load_msg('sample')
        self.msg.get_payload(0).set_payload(s)
        self.assertEqual(self.msg.get_payload(0).get_payload(),
                         'Con cien ca=C3=B1ones por banda, viento en popa a toda vela')

    def test_get_payload(self):
        self.msg = load_msg('sample')
        s = u'La direcci=F3n ha cambiado como pod=E9is comprobar en'
        self.assertTrue(s in self.msg.get_payload(0).get_payload())

    def test_get_payload_decoded(self):
        self.msg = load_msg('sample')
        s = u'La dirección ha cambiado como podéis comprobar en el'
        self.assertTrue(s in self.msg.get_payload(0).get_payload(decode=True))
