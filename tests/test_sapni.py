# encoding: utf-8
# pysap - Python library for crafting SAP's network protocols packets
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# Author:
#   Martin Gallo (@martingalloar)
#   Code contributed by SecureAuth to the OWASP CBAS project
#

# Standard imports
import sys
import socket
import unittest
from threading import Thread
from struct import pack, unpack
from socketserver import BaseRequestHandler, ThreadingTCPServer
# External imports
from scapy.fields import StrField
from scapy.packet import Packet, Raw
# Custom imports
from pysap.SAPNI import (SAPNI, SAPNIStreamSocket, SAPNIServerThreaded,
                         SAPNIServerHandler, SAPNIProxy, SAPNIProxyHandler)


class PySAPBaseServerTest(unittest.TestCase):

    def start_server(self, address, port, handler_cls, server_cls=None):
        if server_cls is None:
            server_cls = ThreadingTCPServer
        self.server = server_cls((address, port), handler_cls,
                                 bind_and_activate=False)
        self.server.allow_reuse_address = True
        self.server.server_bind()
        self.server.server_activate()
        self.server_thread = Thread(target=self.server.serve_forever)
        self.server_thread.daemon = True
        self.server_thread.start()

    def stop_server(self):
        self.server.shutdown()
        self.server.server_close()
        self.server_thread.join(1)


class PySAPNITest(unittest.TestCase):

    test_string = "LALA" * 10

    def test_sapni_building(self):
        """Test SAPNI length field building"""
        # Ensure self.test_string is in bytes format
        if isinstance(self.test_string, str):
            test_string_bytes = self.test_string.encode('utf-8')
        else:
            test_string_bytes = self.test_string

        sapni = SAPNI() / Raw(test_string_bytes)

        sapni_bytes = bytes(sapni)
        sapni_length, = unpack("!I", sapni_bytes[:4])
        self.assertEqual(sapni_length, len(test_string_bytes))
        self.assertEqual(sapni.payload.load, test_string_bytes)

    def test_sapni_dissection(self):
        """Test SAPNI length field dissection"""
        # Ensure self.test_string is in bytes format
        if isinstance(self.test_string, str):
            test_string_bytes = self.test_string.encode('utf-8')
        else:
            test_string_bytes = self.test_string

        data = pack("!I", len(test_string_bytes)) + test_string_bytes
        sapni = SAPNI(data)
        sapni.decode_payload_as(Raw)

        self.assertEqual(sapni.length, len(test_string_bytes))
        self.assertEqual(sapni.payload.load, test_string_bytes)


class SAPNITestHandler(BaseRequestHandler):
    """Basic SAP NI echo server implemented using TCPServer"""

    def handle(self):
        data = self.request.recv(4)
        (length, ) = unpack("!I", data)
        data = self.request.recv(length)

        response_length = pack("!I", len(data))
        self.request.sendall(response_length + data)


class SAPNITestHandlerKeepAlive(SAPNITestHandler):
    """Basic SAP NI keep alive server"""

    def handle(self):
        SAPNITestHandler.handle(self)
        self.request.sendall("\x00\x00\x00\x08NI_PING\x00".encode())


class SAPNITestHandlerClose(SAPNITestHandler):
    """Basic SAP NI server that closes the connection"""

    def handle(self):
        self.request.send(b"")


class PySAPNIStreamSocketTest(PySAPBaseServerTest):

    test_port = 8005
    test_address = "127.0.0.1"
    test_string = "TEST" * 10

    def test_sapnistreamsocket(self):
        """Test SAPNIStreamSocket"""
        self.start_server(self.test_address, self.test_port, SAPNITestHandler)

        sock = socket.socket()
        sock.connect((self.test_address, self.test_port))

        self.client = SAPNIStreamSocket(sock)
        packet = self.client.sr(Raw(self.test_string))
        packet.decode_payload_as(Raw)
        self.client.close()

        self.assertIn(SAPNI, packet)
        self.assertEqual(packet[SAPNI].length, len(self.test_string))
        self.assertEqual(packet.payload.load, self.test_string.encode())

        self.stop_server()

    def test_sapnistreamsocket_base_cls(self):
        """Test SAPNIStreamSocket handling of custom base packet classes"""
        self.start_server(self.test_address, self.test_port, SAPNITestHandler)

        class SomeClass(Packet):
            fields_desc = [StrField("text", None)]

        sock = socket.socket()
        sock.connect((self.test_address, self.test_port))

        self.client = SAPNIStreamSocket(sock, base_cls=SomeClass)
        packet = self.client.sr(Raw(self.test_string))
        self.client.close()

        self.assertIn(SAPNI, packet)
        self.assertIn(SomeClass, packet)
        self.assertEqual(packet[SAPNI].length, len(self.test_string))
        self.assertEqual(packet[SomeClass].text, self.test_string.encode())

        self.stop_server()

    def test_sapnistreamsocket_getnisocket(self):
        """Test SAPNIStreamSocket get nisocket class method"""
        self.start_server(self.test_address, self.test_port, SAPNITestHandler)

        self.client = SAPNIStreamSocket.get_nisocket(self.test_address,
                                                     self.test_port)

        packet = self.client.sr(Raw(self.test_string))
        packet.decode_payload_as(Raw)
        self.client.close()

        self.assertIn(SAPNI, packet)
        self.assertEqual(packet[SAPNI].length, len(self.test_string))
        self.assertEqual(packet.payload.load, self.test_string.encode())

        self.stop_server()

    def test_sapnistreamsocket_without_keep_alive(self):
        """Test SAPNIStreamSocket without keep alive"""
        self.start_server(self.test_address, self.test_port, SAPNITestHandlerKeepAlive)

        sock = socket.socket()
        sock.connect((self.test_address, self.test_port))

        self.client = SAPNIStreamSocket(sock, keep_alive=False)
        packet = self.client.sr(Raw(self.test_string))
        packet.decode_payload_as(Raw)

        # We should receive our packet first
        self.assertIn(SAPNI, packet)
        self.assertEqual(packet[SAPNI].length, len(self.test_string))
        self.assertEqual(packet.payload.load, self.test_string.encode())

        # Then we should get a we should receive a PING
        packet = self.client.recv()

        self.assertIn(SAPNI, packet)
        self.assertEqual(packet[SAPNI].length, len(SAPNI.SAPNI_PING))
        self.assertEqual(packet.payload.load, SAPNI.SAPNI_PING.encode())

        self.client.close()
        self.stop_server()

    def test_sapnistreamsocket_with_keep_alive(self):
        """Test SAPNIStreamSocket with keep alive"""
        self.start_server(self.test_address, self.test_port, SAPNITestHandlerKeepAlive)

        sock = socket.socket()
        sock.connect((self.test_address, self.test_port))

        self.client = SAPNIStreamSocket(sock, keep_alive=True)
        self.client.send(Raw(self.test_string))

        packet = self.client.recv()
        packet.decode_payload_as(Raw)

        # We should receive our packet first
        self.assertIn(SAPNI, packet)
        self.assertEqual(packet[SAPNI].length, len(self.test_string))
        self.assertEqual(packet.payload.load, self.test_string.encode())

        # Then we should get a connection reset if we try to receive from the server
        try:
            data = self.client.recv()
            self.fail(f"Expected an exception, but received data: {data}")
        except Exception as e:
            print(f"Caught exception as expected: {type(e).__name__}: {str(e)}")
            # Test passes if an exception is raised

        self.client.close()
        self.stop_server()

    def test_sapnistreamsocket_close(self):
        """Test SAPNIStreamSocket with a server that closes the connection"""
        self.start_server(self.test_address, self.test_port, SAPNITestHandlerClose)

        sock = socket.socket()
        sock.connect((self.test_address, self.test_port))

        self.client = SAPNIStreamSocket(sock, keep_alive=False)

        with self.assertRaises(socket.error):
            self.client.sr(Raw(self.test_string.encode()))

        self.stop_server()


class SAPNIServerTestHandler(SAPNIServerHandler):
    """Basic SAP NI echo server implemented using SAPNIServer"""

    def handle_data(self):
        self.request.send(self.packet)


class PySAPNIServerTest(PySAPBaseServerTest):

    test_port = 8005
    test_address = "127.0.0.1"
    test_string = "TEST" * 10
    handler_cls = SAPNIServerTestHandler

    def test_sapniserver(self):
        """Test SAPNIServer"""
        self.start_server(self.test_address, self.test_port, self.handler_cls, SAPNIServerThreaded)

        sock = socket.socket()
        sock.connect((self.test_address, self.test_port))

        # Ensure self.test_string is in bytes format
        if isinstance(self.test_string, str):
            test_string_bytes = self.test_string.encode('utf-8')
        else:
            test_string_bytes = self.test_string

        # Send the length of the string followed by the string itself
        sock.sendall(pack("!I", len(test_string_bytes)) + test_string_bytes)

        # Receive the length of the response
        response = sock.recv(4)
        self.assertEqual(len(response), 4)
        ni_length, = unpack("!I", response)
        self.assertEqual(ni_length, len(test_string_bytes) + 4)

        # Receive the actual response
        response = sock.recv(ni_length)
        self.assertEqual(unpack("!I", response[:4])[0], len(test_string_bytes))
        self.assertEqual(response[4:], test_string_bytes)

        sock.close()
        self.stop_server()


class PySAPNIProxyTest(PySAPBaseServerTest):

    test_proxyport = 8005
    test_serverport = 8006
    test_address = "127.0.0.1"
    test_string = "TEST" * 10
    proxyhandler_cls = SAPNIProxyHandler
    serverhandler_cls = SAPNIServerTestHandler

    def start_sapniproxy(self, handler_cls):
        self.proxy = SAPNIProxy(self.test_address, self.test_proxyport,
                                self.test_address, self.test_serverport,
                                handler=handler_cls)
        self.proxy_thread = Thread(target=self.handle_sapniproxy)
        self.proxy_thread.daemon = True
        self.proxy_thread.start()

    def handle_sapniproxy(self):
        self.proxy.handle_connection()

    def stop_sapniproxy(self):
        self.proxy.stop()

    def test_sapniproxy(self):
        self.start_server(self.test_address, self.test_serverport,
                          self.serverhandler_cls, SAPNIServerThreaded)
        self.start_sapniproxy(self.proxyhandler_cls)

        sock = socket.socket()
        sock.connect((self.test_address, self.test_proxyport))
        sock.sendall(pack("!I", len(self.test_string)) + self.test_string.encode())

        response = sock.recv(4)
        self.assertEqual(len(response), 4)
        ni_length, = unpack("!I", response)
        self.assertEqual(ni_length, len(self.test_string) + 4)

        response = sock.recv(ni_length)
        self.assertEqual(unpack("!I", response[:4]), (len(self.test_string), ))
        self.assertEqual(response[4:], self.test_string.encode())

        sock.close()
        self.stop_sapniproxy()
        self.stop_server()

    def test_sapniproxy_process(self):
        self.start_server(self.test_address, self.test_serverport,
                          self.serverhandler_cls, SAPNIServerThreaded)

        class SAPNIProxyHandlerTest(SAPNIProxyHandler):
            def process_client(self, packet):
                return packet / Raw("Client")

            def process_server(self, packet):
                return packet / Raw("Server")

        self.start_sapniproxy(SAPNIProxyHandlerTest)

        sock = socket.socket()
        sock.connect((self.test_address, self.test_proxyport))

        # Ensure self.test_string is in bytes format
        if isinstance(self.test_string, str):
            test_string_bytes = self.test_string.encode('utf-8')
        else:
            test_string_bytes = self.test_string

        # Send the length of the string followed by the string itself
        sock.sendall(pack("!I", len(test_string_bytes)) + test_string_bytes)

        expected_response = test_string_bytes + b"Client" + b"Server"

        # Receive the length of the response
        response = sock.recv(4)
        self.assertEqual(len(response), 4)
        ni_length, = unpack("!I", response)
        self.assertEqual(ni_length, len(expected_response) + 4)

        # Receive the actual response
        response = sock.recv(ni_length)
        self.assertEqual(unpack("!I", response[:4])[0], len(test_string_bytes) + 6)
        self.assertEqual(response[4:], expected_response)

        sock.close()
        self.stop_sapniproxy()
        self.stop_server()

if __name__ == "__main__":
    unittest.main(verbosity=1)
