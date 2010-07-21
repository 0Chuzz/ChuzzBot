#!python3

import unittest
import core.simplebot as simplebot
from .dummyasync import dummy_socket, DummyAsync

class DummyBot(DummyAsync, simplebot.SimpleBot):
    pass

class BasicTest(unittest.TestCase):
    def setUp(self):
        self.client = DummyBot(('', 0), 'utf-8', {})

    def testPing(self):
        pass

