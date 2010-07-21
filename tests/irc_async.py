#!python3

import unittest
import ssl, socket
import logging
from mock import Mock
from core.irc_async import IRCConnection, IRCMessage, Source
from core.irc_async import IRCError


class TestIRCClient(unittest.TestCase):
    def setUp(self):
        self.fake_socket = Mock()
        self.fake_socket.connect_ex = Mock(return_value=0)

    def test_connection(self):
        host = Mock()
        conn = IRCConnection(host)        
        conn.socket = self.fake_socket
        conn.start()
        conn.socket.connect_ex.assert_called_with(host)
        self.fake_socket.reset_mock()

    def test_SSLConnection(self):
        pass

    def test_bind(self):
        host = "useless_stub"
        conn_ev, msg_ev = Mock(), Mock()
        conn = IRCConnection(host)
        conn.socket = self.fake_socket
        conn.bind_events(conn_ev, msg_ev)
        conn.start()
        self.assertTrue(conn_ev.called)
        conn.collect_incoming_data("PING test")
        conn.found_terminator()
        self.assertTrue(msg_ev.called)
        self.fake_socket.reset_mock()


    def testSendMsg(self):
        host = "useless"
        conn = IRCConnection(host)
        conn.socket = self.fake_socket
        outp = "test output\r\n"
        conn.send_msg(outp)
        conn.socket.send.assert_called_with(outp)
        self.fake_socket.reset_mock()

    

class TestIrcMessage(unittest.TestCase):
    valids = [
            ":domino!domino@HUFir.t2.dsl.v.it PRIVMSG #HUF :DIO\r\n",
            "PING irc.azzir.net\r\n"
            ]
    def test_valid_message(self):
        for valid in self.valids:
            try:
                IRCMessage(valid)
            except IRCError as e:
                self.fail(str(e))

