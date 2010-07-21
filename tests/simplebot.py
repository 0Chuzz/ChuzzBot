#!/usr/bin/env python

import unittest
from mock import Mock
from core import simplebot, irc_async

class TestPluggable(unittest.TestCase):#XXX how to test an abstract class? :P
    def test_plugin_creation(self):
        pass

    def test_event_filter(self):
        pass

    def test_publish_command(self):
        pass

    def test_plugin_deletion(self):
        pass


class TestDecorators(unittest.TestCase):
    def test_decor_event(self):
        fake_check = "test"
        fake_func = Mock()
        fake_func.__name__ = "fake_func"
        fake_msg = Mock()
        fake_msg.command = fake_check
        tfunc = simplebot.event_for(fake_check)(fake_func)
        self.assertEqual(tfunc.plug_name, "fake_func")
        self.assertTrue(tfunc(1,2,3).evt_check(fake_msg))
        tfunc(1,2,3).evt_call(1)
        self.assertTrue(fake_func.called)

    def test_decor_command(self):
        fake = Mock()
        tfunc = simplebot.command_for("test")(fake)
        self.assertEqual(tfunc.plug_name, "test")
        self.assertTrue(hasattr(tfunc, "comm_test"))
        tfunc(1,2,3).comm_test()
        self.assertTrue(fake.called)


class TestChatOutput(unittest.TestCase):
    def setUp(self):
        self.exampl = irc_async.IRCMessage("TEST 1 2 :trail\r\n")
        self.outfunc = Mock()
        self.do = simplebot.ChatOutput(self.outfunc)

    def tearDown(self):
        self.outfunc.reset_mock()

    def test_send_implicit_trail(self):
        self.do.raw("TEST", "1","2","trail")
        self.outfunc.assert_called_with(self.exampl)

    def test_send_explicit_trail(self):
        self.do.raw_trail("TEST", "1","2", trail="trail")
        self.outfunc.assert_called_with(self.exampl)

    def test_send_nick(self):
        pass

    def test_send_custom(self):
        self.do.test("1","2","trail")
        self.outfunc.assert_called_with(self.exampl)

    def test_error_on_send(self):
        pass

    def test_send_privmsg(self):
        pass

    def test_send_multiline(self):
        pass

    def test_send_ml_block(self):
        pass


class TestSimpleBot(unittest.TestCase):
    def test_creation(self):
        pass

    def test_load_module(self):
        pass

    def test_reload_module(self):
        pass

    def test_unload_module(self):
        pass

    def test_duplicate_module(self):
        pass

    def test_modules_conflict(self):
        pass

    def test_plugin_crash(self):
        pass


