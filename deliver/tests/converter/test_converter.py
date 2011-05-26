# -*- coding: utf-8 -*-
from deliver.tests.test_base import BaseTest, load_msg, load_all_msg

class ConverterTest(BaseTest):
    '''Tests for the UnicodeMessage class'''

    def setUp(self):
        super(ConverterTest,self).setUp()
        self.msg = load_msg('sample3')

    def get_text(self, decode=False):
        return self.msg.get_payload(0).get_payload(decode=decode)

    def get_clean_text(self, forbidden_words):
        return self.msg.get_payload(0).get_clean_payload(forbidden_words)

    def set_text(self, payload):
        self.msg.get_payload(0).set_payload(payload)

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

    def test_replace_header_no_header(self):
        s = u'quoted-printable'
        self.msg.replace_header('Content-Transfer-Encoding', s)
        self.assertEqual(self.msg['Content-Transfer-Encoding'], s)

    def _test_get(self, s, encoded):
        self.assertEqual(self.get_text(decode=True), s)
        self.assertEqual(self.get_text(), encoded)

    def _test_set(self, s, encoded):
        self.set_text(s)
        self._test_get(s, encoded)

    def test_set_payload(self):
        s = u'El perro del hortelano'
        self.msg = load_msg('sample')
        self._test_set(s, s)

    def test_set_payload_special_chars(self):
        s = u'Con cien cañones por banda, viento en popa a toda vela'
        self.msg = load_msg('sample')
        self._test_set(s, u'Con cien ca=F1ones por banda, viento en popa a toda vela')

    def test_set_payload_utf8(self):
        s = u'Con cien cañones por banda, viento en popa a toda vela'
        self.msg = load_msg('sample')
        self.msg.get_payload(0).set_charset('utf-8')
        self._test_set(s, u'Con cien ca=C3=B1ones por banda, viento en popa a toda vela')

    def test_set_payload_base64(self):
        s = u'Con cien cañones por banda, viento en popa a toda vela'
        self.msg = load_msg('sample4')
        self._test_set(s, u'Con cien ca=F1ones por banda, viento en popa a toda vela')

    def test_set_payload_base64_utf8(self):
        s = u'Con cien cañones por banda, viento en popa a toda vela'
        self.msg = load_msg('sample5')
        self._test_set(s, u'Con cien ca=C3=B1ones por banda, viento en popa a toda vela')

    def test_set_payload_empty(self):
        s = u'Con cien cañones por banda, viento en popa a toda vela'
        self.msg = load_msg('sample6')
        self._test_set(s, u'Con cien ca=F1ones por banda, viento en popa a toda vela')

    def test_get_payload(self):
        self.msg = load_msg('sample')
        s = u'La direcci=F3n ha cambiado como pod=E9is comprobar en'
        self.assertTrue(s in self.get_text())

    def test_get_payload_decoded(self):
        self.msg = load_msg('sample')
        s = u'La dirección ha cambiado como podéis comprobar en el'
        self.assertTrue(s in self.get_text(decode=True))

    def test_get_payload_base64(self):
        self.msg = load_msg('sample4')
        self._test_get(u'á\n', u'4Qo=')

    def test_get_payload_base64_utf8(self):
        self.msg = load_msg('sample5')
        self._test_get(u'á', u'w6E=')

    def test_get_payload_empty(self):
        self.msg = load_msg('sample6')
        self._test_get(u'\n', u'\n')

    def test_clean_word_no_replace(self):
        self.assertEqual(self.msg._clean_word(u'panic', {}), u'panic')

    def test_clean_word_replace(self):
        self.assertEqual(self.msg._clean_word(u'panic', {u'panic' : u'don\'t'}), u'don\'t')

    def test_clean_word_replace_case(self):
        self.assertEqual(self.msg._clean_word(u'Panic', {u'panic' : u'don\'t'}), u'don\'t')

    def test_clean_word_replace_special_chars(self):
        self.assertEqual(self.msg._clean_word(u'Pánico', {u'pánico' : u'don\'t'}), u'don\'t')

    def test_clean_word_surrounded(self):
        self.assertEqual(self.msg._clean_word(u'*Pánico*?', {u'pánico' : u'don\'t'}), u'*don\'t*?')

    def test_get_clean_payload(self):
        words = self.config['forbidden_words']
        payload = self.get_clean_text(words)

        for word in words.keys():
            self.assertFalse(word in payload, 'word %s was not removed' % word)
        for replacement in words.values():
            self.assertTrue(replacement in payload, 'word %s was not inserted' % word)

    def test_walk(self):
        for mail in load_all_msg():
            list(mail.walk())
