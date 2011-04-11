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

    def test_update_nothing_new(self):
        self.reader.new_messages.return_value = []
        self.distributor.update()

        self.reader.connect.assert_called_once_with()
        self.reader.new_messages.assert_called_once_with()
        self.reader.disconnect.assert_called_once_with()
