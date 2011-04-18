# -*- coding: utf-8 -*-
from test_base import BaseTest

from deliver.members import MemberMgr

class MemberMgrTest(BaseTest):

    def setUp(self):
        super(MemberMgrTest,self).setUp()
        self.memberMgr = MemberMgr(self.config)

    def test_active_members(self):
        self.assertEqual(self.memberMgr.active_members(sender = u'TEST@mail.com'),
                          [u'loser@mail.com', u'stranger@mail.com'])

    def test_find_member_not_found(self):
        self.assertEqual(self.memberMgr.find_member(''), None)

    def test_find_member(self):
        member = self.memberMgr.find_member(u'stranger@mail.com')
        self.assertEqual(member['name'], u'Niño Él')
        self.assertEqual(member['aliases'], [u'Sí', u'Quizás'])

    def test_find_member_special_chars(self):
        member = self.memberMgr.find_member(u'test@mail.com')
        self.assertEqual(member['name'], u'Name')
        self.assertEqual(member['aliases'], [u'Alternative 1', u'Alt 2'])

    def test_iswhitelisted_fail(self):
        self.assertFalse(self.memberMgr.iswhitelisted(''))

    def test_iswhitelisted(self):
        self.assertTrue(self.memberMgr.iswhitelisted('whitelist@HOST.com'))

    def test_choose_name_no_aliases(self):
        self.assertEquals(self.memberMgr.choose_name(
                self.memberMgr.find_member(u'inactivE@mail.com')), u'MIA')

    def test_choose_name(self):
        self.assertTrue(self.memberMgr.choose_name(
                self.memberMgr.find_member(u'tEst@mail.com')) in
                        [u'Name', u'Alternative 1', u'Alt 2'])
