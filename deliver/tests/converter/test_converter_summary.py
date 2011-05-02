# -*- coding: utf-8 -*-
from deliver.tests.test_base import BaseTest, load_msg

from deliver.converter.digest import DigestMessage

class ConverterDigestTest(BaseTest):
    '''Tests for the DigestMessage class'''

    def setUp(self):
        super(ConverterDigestTest,self).setUp()
        self.msg = DigestMessage([])

    def test_find_text(self):
        self.assertEqual(self.msg._find_text(load_msg('sample5')), u'á')

    def test_find_text_empty(self):
        self.assertEqual(self.msg._find_text(load_msg('sample6')), u'\n')

    def test_merge_mails_empty(self):
        self.assertEqual(self.msg._merge_mails([]), u'')

    def _load_mails(self, *fileNames):
        return [load_msg(f) for f in fileNames]

    def test_merge_mails_(self):
        split = self.msg._merge_mails(self._load_mails('sample5', 'sample6', 'sample7')).split('\n')
        self.assertEqual(split.count(u'á'), 2)
        self.assertEqual(split.count(u''), 9)
        self.assertEqual(split.count(u'*' * 75), 2)

    def test_build_mail(self):
        msg = DigestMessage(self._load_mails('sample', 'sample5', 'sample7'))
        self.assertTrue('Digest for' in msg['Subject'])
        self.assertFalse(msg.id is None)
        self.assertTrue('text/plain' in msg['Content-Type'])
        self.assertEqual(msg['Content-Transfer-Encoding'], 'quoted-printable')
        self.assertFalse(msg['Date'] is None)
