from test_base import BaseTest

from deliver.distribute import MemberMgr

class MemberMgrTest(BaseTest):

    def setUp(self):
        super(MemberMgrTest,self).setUp()
        self.memberMgr = MemberMgr(self.config)

    def test_active_members(self):
        self.assertEqual(self.memberMgr.active_members(sender = 'TEST@mail.com'),
                          [u'loser@mail.com'])

    def test_find_member_not_found(self):
        self.assertEqual(self.memberMgr.find_member(''), None)

    def test_find_member(self):
        member = self.memberMgr.find_member('test@mail.com')
        self.assertEqual(member['name'], 'Name')
        self.assertEqual(member['aliases'], ['Alternative 1', 'Alt 2'])

    def test_iswhitelisted_fail(self):
        self.assertFalse(self.memberMgr.iswhitelisted(''))

    def test_iswhitelisted(self):
        self.assertTrue(self.memberMgr.iswhitelisted('whitelist@HOST.com'))

    def test_choose_name_no_aliases(self):
        self.assertEquals(self.memberMgr.choose_name(
                self.memberMgr.find_member('inactivE@mail.com')), 'MIA')

    def test_choose_name(self):
        self.assertTrue(self.memberMgr.choose_name(
                self.memberMgr.find_member('tEst@mail.com')) in
                        ['Name', 'Alternative 1', 'Alt 2'])
