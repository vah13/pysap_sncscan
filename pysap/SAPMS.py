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

# External imports
from scapy.layers.inet import TCP
from scapy.packet import Packet, bind_layers
from scapy.fields import (ByteField, ConditionalField, StrFixedLenField, FlagsField,
                          IPField, ShortField, IntField, StrField, PacketListField,
                          FieldLenField, PacketField, StrLenField, IntEnumField,
                          ByteEnumKeysField, ShortEnumKeysField, Field,
                          PacketLenField, XByteField, SignedIntField)
from scapy.layers.inet6 import IP6Field
# Custom imports
from pysap.SAPNI import SAPNI
from pysap.utils.fields import (PacketNoPadded, IntToStrField, StrNullFixedLenPaddedField,
                                StrNullFixedLenField)


# Message Server Domain values
ms_domain_values = {
    0x00: "ABAP",
    0x01: "J2EE",
    0x02: "JSTARTUP",
}
"""Message Server Domain values"""


# Inverse dictionary for obtaining the value from a given domain name
ms_domain_values_inv = {v: k for k, v in list(ms_domain_values.items())}


# Message Server Flag values
ms_flag_values = {
    0x00: "MS_UNKNOWN",
    0x01: "MS_ONE_WAY",  # One way messages are sent from the client to server and doesn't trigger a response
                         # from the server
    0x02: "MS_REQUEST",
    0x03: "MS_REPLY",
    0x04: "MS_ADMIN",
}
"""Message Server Flag values"""


# Message Server IFlag values
ms_iflag_values = {
    0x00: "MS_UNKNOWN",
    0x01: "MS_SEND_NAME",
    0x02: "MS_SEND_TYPE",
    0x03: "MS_LOGIN",
    0x04: "MS_LOGOUT",
    0x05: "MS_ADM_OPCODES",
    0x06: "MS_MOD_MSGTYPES",
    0x07: "MS_SEND_TYPE_ONCE",
    0x08: "MS_LOGIN_2",
    0x09: "MS_MOD_STATE",
    0x0a: "MS_J2EE_LOGIN",
    0x0c: "MS_J2EE_SEND_TO_CLUSTERID",
    0x0d: "MS_J2EE_SEND_BROADCAST",
    0x0e: "MS_SEND_TYPE_ACK",
    0x0f: "MS_J2EE_LOGIN_2",
    0x10: "MS_SEND_SERVICE",
    0x11: "MS_J2EE_LOGIN_3",
    0x12: "MS_J2EE_LOGIN_4",
}
"""Message Server IFlag values"""


# Message Server Error values
ms_errorno_values = {
    0: "MSERECONNECTION",
    1: "MSENISELWRITE",
    2: "MSENISELREAD",
    3: "MSENIQUEUE",
    4: "MSENILAYER",
    71: "MSETESTSOFTSHUTDOWN",
    72: "MSENOTINIT",
    73: "MSEALREADYINIT",
    74: "MSEINVHDL",
    75: "MSEWRONGSERVER",
    76: "MSEMOREDATA",
    77: "MSESNDTYPEFAILED",
    78: "MSEDUPKEY",
    79: "MSESOFTSHUTDOWN",
    81: "MSENOMEM",
    82: "MSEHEADERINCOMPLETE",
    83: "MSETYPESNOTALLOWED",
    84: "MSEACCESSDENIED",
    85: "MSEWRITEINCOMPLETE",
    86: "MSEREADINCOMPLETE",
    87: "MSEADMIN",
    88: "MSESOCKTOOLARGE",
    89: "MSENOSLOTFREE",
    90: "MSESHUTDOWN",
    91: "MSEREPLYTOOLARGE",
    92: "MSEWRONGVERSION",
    93: "MSEMSGDESTROYED",
    94: "MSENOTUNIQUE",
    95: "MSEPARTNERUNKNOWN",
    96: "MSEPARTNERDIED",
    97: "MSEWRONGTYPE",
    98: "MSEWRONGNAME",
    99: "MSEWAKEUP",
    100: "MSENOTFOUND",
    101: "MSEINVAL",
    102: "MSENOMSG",
    103: "MSEINTERN",
}
"""Message Server Error values"""


# Message Server Administration messages type values
ms_adm_type_values = {
    1: "ADM_REQUEST",
    2: "ADM_REPLY",
}
"""Message Server Administration messages type values"""


# Message Server Administration messages opcode values
ms_adm_opcode_values = {
    0x00: "AD_GENERAL",
    0x01: "AD_PROFILE",  # *
    0x02: "AD_WPSTAT",
    0x03: "AD_QUEUE",
    0x04: "AD_STARTSTOP",
    0x05: "AD_WPCONF",
    0x06: "AD_USRLST",
    0x07: "AD_WPKILL",
    0x08: "AD_TIMEINFO",  # *
    0x09: "AD_TM_RECONNECT",
    0x0a: "AD_ALRT_GET_STATE",
    0x0b: "AD_ALRT_OPERATION",
    0x0c: "AD_ALRT_SET_PARAM",
    0x0d: "AD_DB_RECONNECT",
    0x0e: "AD_ECHO",  # *
    0x0f: "AD_MSGSERVER",  # *
    0x10: "AD_WPCONF2",
    0x11: "AD_GENERAL2",
    0x12: "AD_SET_LIST_PARAM",
    0x13: "AD_DUMP_STATUS",
    0x14: "AD_RZL",
    0x15: "AD_RZL_STRG",  # *
    0x16: "AD_COUNT_WPS",
    0x17: "AD_QUEUE2",
    0x19: "AD_EM",
    0x1a: "AD_ES",
    0x1b: "AD_SHUTDOWN_STATE",
    0x1c: "AD_SHUTDOWN_INFO",
    0x1d: "AD_SHUTDOWN_ERROR",
    0x1f: "AD_DISPLACE",
    0x20: "AD_GET_TIMETAB",
    0x21: "AD_SET_TIMETAB",
    0x28: "AD_MSBUF",
    0x29: "AD_ARFC_NOREQ",
    0x2a: "AD_ENQID_INFO",
    0x2b: "AD_DEL_USER",
    0x2c: "AD_SPO_ADM",
    0x2d: "AD_NTAB_SYNC",
    0x2e: "AD_SHARED_PARAMETER",  # *
    0x2f: "AD_RESET_TRACE",
    0x30: "AD_RESET_USR02",
    0x31: "AD_WALL_CREATE",
    0x32: "AD_WALL_DELETE",
    0x33: "AD_WALL_MODIFY",
    0x34: "AD_SERVER_STATE",
    0x3c: "AD_SELFIDENT",  # *
    0x3d: "AD_DP_TRACE_CHANGE",
    0x3e: "AD_DP_DUMP_NIHDL",
    0x3f: "AD_DP_CALL_DELAYED",
    0x40: "AD_GW_ADM",
    0x41: "AD_DP_WAKEUP_MODE",
    0x42: "AD_VMC_SYS_EVENT",
    0x43: "AD_SHARED_PARAM_ALL_WPS",
    0x44: "AD_SECSESSION_UPDATE",
    0x45: "AD_SECSESSION_TERMINATE",
    0x46: "AD_ASRF_REQUEST",
    0x47: "AD_GET_NILIST",
    0x48: "AD_LOAD_INFO",
    0x49: "AD_TEST",
    0x4a: "AD_HANDLE_ACL",
    0x4b: "AD_PROFILE2",  # from here, extracted from bin analysis
    0x4c: "AD_RSCP_ASYNC",
    0x4d: "AD_BATCH_INFO",
    0x4e: "AD_SOFT_CANCEL",
    0x55: "AD_SYNC_LOAD_FMT",
    0x56: "AD_GET_NILIST_PORT",
    0x5a: "AD_UNKNOWN",  # added for avoiding error on dict access in some cases
}
"""Message Server Administration messages opcode values"""


# Message Server Administration Messages AD_RZL_STRG string types values
ms_adm_rzl_strg_type_values = {
    10: "STRG_TYPE_READALL",
    11: "STRG_TYPE_READALL_I",
    12: "STRG_TYPE_READALL_C",
    13: "STRG_TYPE_READALL_LC",
    15: "STRG_TYPE_READALL_OFFSET_I",
    16: "STRG_TYPE_READALL_OFFSET_C",
    17: "STRG_TYPE_READALL_OFFSET_LC",
    20: "STRG_TYPE_READALL_OFFSET",
    21: "STRG_TYPE_READ_I",
    22: "STRG_TYPE_READ_C",
    23: "STRG_TYPE_READ_LC",
    31: "STRG_TYPE_WRITE_I",
    32: "STRG_TYPE_WRITE_C",
    33: "STRG_TYPE_WRITE_LC",
    41: "STRG_TYPE_DEL_I",
    42: "STRG_TYPE_DEL_C",
    43: "STRG_TYPE_DEL_LC",
    51: "STRG_TYPE_CREATE_I",
    52: "STRG_TYPE_CREATE_C",
    53: "STRG_TYPE_CREATE_LC",
    90: "STRG_TYPE_DUMP",
}
"""Message Server Administration Messages AD_RZL_STRG string types values"""


# Message Server OpCode values
ms_opcode_values = {
    0: "MS_DP_ADM",
    1: "MS_SERVER_CHG",
    2: "MS_SERVER_ADD",
    3: "MS_SERVER_SUB",
    4: "MS_SERVER_MOD",
    5: "MS_SERVER_LST",
    6: "MS_CHANGE_IP",
    7: "MS_SET_SECURITY_KEY",
    8: "MS_GET_SECURITY_KEY",
    9: "MS_GET_SECURITY_KEY2",
    10: "MS_GET_HWID",
    11: "MS_INCRE_TRACE",
    12: "MS_DECRE_TRACE",
    13: "MS_RESET_TRACE",
    14: "MS_ACT_STATISTIC",
    15: "MS_DEACT_STATISTIC",
    16: "MS_RESET_STATISTIC",
    17: "MS_GET_STATISTIC",
    18: "MS_DUMP_NIBUFFER",
    19: "MS_RESET_NIBUFFER",
    20: "MS_OPEN_REQ_LST",
    21: "MS_SERVER_INFO",
    22: "MS_SERVER_LIST",
    23: "MS_SERVER_ENTRY",
    24: "MS_DOMAIN_INFO",
    25: "MS_DOMAIN_LIST",
    26: "MS_DOMAIN_ENTRY",
    27: "MS_MAP_URL_TO_ADDR",
    28: "MS_GET_CODEPAGE",
    29: "MS_SOFT_SHUTDOWN",
    30: "MS_DUMP_INFO",
    31: "MS_FILE_RELOAD",
    32: "MS_RESET_DOMAIN_CONN",
    33: "MS_NOOP",
    34: "MS_SET_TXT",
    35: "MS_GET_TXT",
    36: "MS_COUNTER_CREATE",
    37: "MS_COUNTER_DELETE",
    38: "MS_COUNTER_INCREMENT",
    39: "MS_COUNTER_DECREMENT",
    40: "MS_COUNTER_REGISTER",
    41: "MS_COUNTER_GET",
    42: "MS_COUNTER_LST",
    43: "MS_SET_LOGON",
    44: "MS_GET_LOGON",
    45: "MS_DEL_LOGON",
    46: "MS_SERVER_DISC",
    47: "MS_SERVER_SHUTDOWN",
    48: "MS_SERVER_SOFT_SHUTDOWN",
    49: "MS_J2EE_CLUSTERNODE_CHG",
    50: "MS_J2EE_CLUSTERNODE_ADD",
    51: "MS_J2EE_CLUSTERNODE_SUB",
    52: "MS_J2EE_CLUSTERNODE_MOD",
    53: "MS_J2EE_CLUSTERNODE_LST",
    54: "MS_J2EE_SERVICE_REG",
    55: "MS_J2EE_SERVICE_UNREG",
    56: "MS_J2EE_SERVICE_LST",
    57: "MS_J2EE_SERVICE_ADD",
    58: "MS_J2EE_SERVICE_SUB",
    59: "MS_J2EE_SERVICE_MOD",
    60: "MS_J2EE_MOD_STATE",
    61: "MS_J2EE_SERVICE_GET",
    62: "MS_J2EE_SERVICE_REG2",
    63: "MS_NITRACE_SETGET",
    64: "MS_SERVER_LONG_LIST",
    65: "MS_J2EE_DEBUG_ENABLE",
    66: "MS_J2EE_DEBUG_DISABLE",
    67: "MS_SET_PROPERTY",
    68: "MS_GET_PROPERTY",
    69: "MS_DEL_PROPERTY",
    70: "MS_IP_PORT_TO_NAME",
    71: "MS_CHECK_ACL",
    72: "MS_LICENSE_SRV",
    74: "MS_SERVER_TEST_SOFT_SHUTDOWN",
    75: "MS_J2EE_RECONNECT_P1",
    76: "MS_J2EE_RECONNECT_P2",
}
"""Message Server OpCode values"""


# Message Server OpCode Error Values
ms_opcode_error_values = {
    0: "MSOP_OK",
    1: "MSOP_UNKNOWN_OPCODE",
    2: "MSOP_NOMEM",
    3: "MSOP_SECURITY_KEY_NOTSET",
    4: "MSOP_UNKNOWN_CLIENT",
    5: "MSOP_ACCESS_DENIED",
    6: "MSOP_REQUEST_REQUIRED",
    7: "MSOP_NAME_REQUIRED",
    8: "MSOP_GET_HWID_FAILED",
    9: "MSOP_SEND_FAILED",
    10: "MSOP_UNKNOWN_DOMAIN",
    11: "MSOP_UNKNOWN_SERVER",
    12: "MSOP_NO_DOMAIN_SERVER",
    13: "MSOP_INVALID_URL",
    14: "MSOP_UNKNOWN_DUMP_REQ",
    15: "MSOP_FILENOTFOUND",
    16: "MSOP_UNKNOWN_RELOAD_REQ",
    17: "MSOP_FILENOTDEFINED",
    18: "MSOP_CONVERT_FAILED",
    19: "MSOP_NOTSET",
    20: "MSOP_COUNTER_EXCEEDED",
    21: "MSOP_COUNTER_NOTFOUND",
    22: "MSOP_COUNTER_DELETED",
    23: "MSOP_COUNTER_EXISTS",
    24: "MSOP_EINVAL",
    25: "MSOP_NO_J2EE_CLUSTERNODE",
    26: "MSOP_UNKNOWN_PROPERTY",
    27: "MSOP_UNKNOWN_VERSION",
    28: "MSOP_ICTERROR",
    29: "MSOP_KERNEL_INCOMPATIBLE",
    30: "MSOP_NIACLCREATE_FAILED",
    31: "MSOP_NIACLSYNTAX_ERROR",
}
"""Message Server OpCode Error Values"""


# Message Server Property ID Values
ms_property_id_values = {
    1: "MS_PROPERTY_TEXT",
    2: "MS_PROPERTY_VHOST",
    3: "MS_PROPERTY_IPADR",
    4: "MS_PROPERTY_PARAM",  # ZDI Bugs are here
    5: "MS_PROPERTY_SERVICE",
    6: "MS_PROPERTY_DELALT",
    7: "Release information"
}
"""Message Server Property ID Values"""


# Message Server Dump Info ID Values
ms_dump_command_values = {
    1: "MS_DUMP_MSADM",
    2: "MS_DUMP_CON",
    3: "MS_DUMP_PARAMS",
    4: "MS_DUMP_ALL_CLIENTS",
    5: "MS_DUMP_ALL_SERVER",
    6: "MS_DUMP_ALL_DOMAIN",
    7: "MS_DUMP_DOMAIN_CONN",
    8: "MS_DUMP_RELEASE",
    9: "MS_DUMP_SIZEOF",
    10: "MS_DUMP_FIADM",
    11: "MS_DUMP_FICON",
    12: "MS_DUMP_COUNTER",
    13: "MS_DUMP_STATISTIC",
    14: "MS_DUMP_NIBUF",
    15: "MS_DUMP_URLMAP",
    16: "MS_DUMP_URLPREFIX",
    17: "MS_DUMP_URLHANDLER",
    18: "MS_DUMP_NOSERVER",
    19: "MS_DUMP_ACLINFO",
    20: "MS_DUMP_PERMISSION_TABLE",
    21: "MS_DUMP_J2EE_CLUSTER_STAT",
    22: "MS_DUMP_ACL_FILE_EXT",
    23: "MS_DUMP_ACL_FILE_INT",
    24: "MS_DUMP_ACL_FILE_ADMIN",
    25: "MS_DUMP_ACL_FILE_EXTBND",
    26: "MS_DUMP_ACL_FILE_HTTP",
    27: "MS_DUMP_ACL_FILE_HTTPS",
}
"""Message Server Dump Info ID Values"""


# Message Server File Reload values
ms_file_reload_values = {
    1: "MS_RELOAD_CLIENT_TAB",
    2: "MS_RELOAD_SERVER_TAB",
    3: "MS_RELOAD_DOMAIN_TAB",
    4: "MS_RELOAD_URLMAP",
    5: "MS_RELOAD_URLPREFIX",
    6: "MS_RELOAD_ACL_INFO",
    7: "MS_RELOAD_PERMISSION_TABLE",
    8: "MS_RELOAD_STOC",
    9: "MS_RELOAD_ACL_FILE_EXT",
    10: "MS_RELOAD_ACL_FILE_INT",
    11: "MS_RELOAD_ACL_FILE_ADMIN",
    12: "MS_RELOAD_ACL_FILE_EXTBND",
    13: "MS_RELOAD_ACL_FILE_HTTP",
    14: "MS_RELOAD_ACL_FILE_HTTPS",
}
"""Message Server File Reload values"""


# Message Server Logon type values
ms_logon_type_values = {
    0: "MS_LOGON_DIAG_LB",
    1: "MS_LOGON_DIAG_LBS",
    2: "MS_LOGON_DIAG",
    3: "MS_LOGON_DIAGS",
    4: "MS_LOGON_RFC",
    5: "MS_LOGON_RFCS",
    6: "MS_LOGON_HTTP",
    7: "MS_LOGON_HTTPS",
    8: "MS_LOGON_FTP",
    9: "MS_LOGON_SMTP",
    10: "MS_LOGON_NNTP",
    11: "MS_LOGON_DIAG_E",
    12: "MS_LOGON_DIAGS_E",
    13: "MS_LOGON_RFC_E",
    14: "MS_LOGON_RFCS_E",
    15: "MS_LOGON_HTTP_E",
    16: "MS_LOGON_HTTPS_E",
    17: "MS_LOGON_FTP_E",
    18: "MS_LOGON_SMTP_E",
    19: "MS_LOGON_NNTP_E",
    20: "MS_LOGON_J2EE",
    21: "MS_LOGON_J2EES",
    22: "MS_LOGON_J2EE_E",
    23: "MS_LOGON_J2EES_E",
    24: "MS_LOGON_P4",
    25: "MS_LOGON_P4S",
    26: "MS_LOGON_IIOP",
    27: "MS_LOGON_IIOPS",
    28: "MS_LOGON_SDM",
    29: "MS_LOGON_TELNET",
    30: "MS_LOGON_DEBUG",
    31: "MS_LOGON_DPROXY",
    32: "MS_LOGON_P4HTTP",
    33: "MS_LOGON_HTTPRI",
    34: "MS_LOGON_HTTPSRI",
    35: "MS_LOGON_J2EERI",
    36: "MS_LOGON_J2EESRI",
    37: "MS_LOGON_TRXNS",
}
"""Message Server Logon type values"""


ms_client_status_values = {
    0: "MS_STATE_UNKNOWN",
    1: "ACTIVE",
    2: "INACTIVE",
    3: "MS_STATE_SHUTDOWN",
    4: "MS_STATE_STOP",
    5: "MS_STATE_STARTING",
    6: "MS_STATE_INIT",
}
"""Message Server Client status values"""


dp_prio_values = {
    0: "LOW",
    1: "MEDIUM",
    2: "HIGH",
}
"""Message Server Dispatcher Info Priority values"""


dp_type_values = {
    0: "INVALID",
    1: "LOCAL",
    2: "BY_NAME",
    3: "BY_TYPE",
    4: "MSG_SRV",
}
"""Message Server Dispatcher Info Type values"""


dp_agent_type_values = {
    0: "INVALID",
    1: "DISP",
    2: "GATEWAY",
    3: "ICMAN",
    4: "TERMINAL",
    5: "MSG",
    6: "WORKER",
    7: "EXT-EVT",
    8: "STARTSRV",
    9: "DPMON",
    10: "ICMON",
}
"""Message Server Dispatcher Info Agent Type values"""


dp_worker_type_values = {
    0: "NOWP",
    1: "DIA",
    2: "UPD",
    3: "ENQ",
    4: "BTC",
    5: "SPO",
    6: "UP2",
}
"""Message Server Dispatcher Info Worker Type values"""


dp_req_handler_values = {
    2: "REQ_HANDLER_GUI",
    8: "REQ_HANDLER_UPDATE",
    10: "REQ_HANDLER_UPDATE2",
    12: "REQ_HANDLER_UPDATE_ADMIN",
    13: "REQ_HANDLER_UPDATE_ADMIN_RESP",
    38: "REQ_HANDLER_RPC",
    40: "REQ_HANDLER_ADM",
    41: "REQ_HANDLER_ADM_RESP",
    42: "REQ_HANDLER_MSG_SERVER",
    43: "REQ_HANDLER_MSG_SERVER_RESP",
    44: "REQ_HANDLER_BTC",
    80: "REQ_HANDLER_SHUTDOWN",
    84: "REQ_HANDLER_PROCESS",
    86: "REQ_HANDLER_REGISTER_PROCESS",
    111: "REQ_HANDLER_AUTOJAVA_RESP",
    112: "REQ_HANDLER_VMC_RUNTIME",
    124: "REQ_HANDLER_SERVER_STARTUP",
    130: "REQ_HANDLER_SUSPEND_SERVER",
    132: "REQ_HANDLER_RESUME_SERVER",
}
"""Message Server Dispatcher Info Request Handler values"""


class SAPMSAdmRecord(PacketNoPadded):
    """SAP Message Server Administration Record packet

    Packet for Message Server administration records. Each administration
    package has a variable number of records, each one specifies an operation
    to execute.
    """
    name = "SAP Message Server Adm Record"
    fields_desc = [
        ByteEnumKeysField("opcode", 0x00, ms_adm_opcode_values),
        ByteField("serial_number", 0x00),
        ByteField("executed", 0x00),
        ByteField("errorno", 0x00),  # TODO: Look for error names
        ConditionalField(StrFixedLenField("record", None, 75), lambda pkt:pkt.opcode not in [0x01, 0x15, 0x2e] and pkt.executed == 0x01),
        ConditionalField(StrFixedLenField("record_pad", None, 25), lambda pkt:pkt.opcode not in [0x01, 0x15, 0x2e] and pkt.executed == 0x01),
        ConditionalField(StrFixedLenField("record", None, 100), lambda pkt:pkt.opcode not in [0x01, 0x15, 0x2e] and pkt.executed == 0x00),

        # TODO: Add more opcodes fields

        # AD_PROFILE and AD_SHARED_PARAMETER fields
        ConditionalField(StrNullFixedLenPaddedField("parameter", "", 100), lambda pkt:pkt.opcode in [0x01, 0x2e]),

        # AD_RZL_STRG opcode
        ConditionalField(ByteEnumKeysField("rzl_strg_type", 1, ms_adm_rzl_strg_type_values), lambda pkt:pkt.opcode in [0x15]),
        ConditionalField(ByteField("rzl_strg_name_length", 0), lambda pkt:pkt.opcode in [0x15]),
        ConditionalField(ByteField("rzl_strg_value_offset", 0), lambda pkt:pkt.opcode in [0x15]),
        ConditionalField(ByteField("rzl_strg_value_length", 0), lambda pkt:pkt.opcode in [0x15]),
        ConditionalField(StrFixedLenField("rzl_strg_name", None, 20), lambda pkt:pkt.opcode in [0x15]),
        ConditionalField(IntField("rzl_strg_uptime", 0), lambda pkt:pkt.opcode in [0x15] and pkt.rzl_strg_type in [11, 15, 21, 31, 41, 51]),
        ConditionalField(IntField("rzl_strg_integer1", 0), lambda pkt:pkt.opcode in [0x15] and pkt.rzl_strg_type in [11, 15, 21, 31, 41, 51]),
        ConditionalField(IntField("rzl_strg_delay", 0), lambda pkt:pkt.opcode in [0x15] and pkt.rzl_strg_type in [11, 15, 21, 31, 41, 51]),
        ConditionalField(IntField("rzl_strg_integer3", 0), lambda pkt:pkt.opcode in [0x15] and pkt.rzl_strg_type in [11, 15, 21, 31, 41, 51]),
        ConditionalField(IntField("rzl_strg_users", 0), lambda pkt:pkt.opcode in [0x15] and pkt.rzl_strg_type in [11, 15, 21, 31, 41, 51]),
        ConditionalField(IntField("rzl_strg_quality", 0), lambda pkt:pkt.opcode in [0x15] and pkt.rzl_strg_type in [11, 15, 21, 31, 41, 51]),
        ConditionalField(IntField("rzl_strg_integer6", 0), lambda pkt:pkt.opcode in [0x15] and pkt.rzl_strg_type in [11, 15, 21, 31, 41, 51]),
        ConditionalField(IntField("rzl_strg_integer7", 0), lambda pkt:pkt.opcode in [0x15] and pkt.rzl_strg_type in [11, 15, 21, 31, 41, 51]),
        ConditionalField(IntField("rzl_strg_integer8", 0), lambda pkt:pkt.opcode in [0x15] and pkt.rzl_strg_type in [11, 15, 21, 31, 41, 51]),
        ConditionalField(IntField("rzl_strg_integer9", 0), lambda pkt:pkt.opcode in [0x15] and pkt.rzl_strg_type in [11, 15, 21, 31, 41, 51]),
        ConditionalField(StrFixedLenField("rzl_strg_value", None, 40), lambda pkt:pkt.opcode in [0x15] and pkt.rzl_strg_type not in [11, 15, 21, 31, 41, 51]),
        ConditionalField(StrFixedLenField("rzl_strg_padd2", None, 36), lambda pkt:pkt.opcode in [0x15]),
    ]


class SAPMSClient1(PacketNoPadded):
    """SAP Message Server Client packet version 1

    Packet that contains information about a client of the Message Server
    service. This packet is for version 1, which has been seen only on old
    releases (SAP NW 2004s).
    """
    name = "SAP Message Server Client version 1"
    fields_desc = [
        StrFixedLenField("client", None, 20),
        StrFixedLenField("host", None, 20),
        StrFixedLenField("service", None, 20),
        FlagsField("msgtype", 0, 8, ["ICM", "ATP", "UP2", "SPO", "BTC", "ENQ", "UPD", "DIA"]),
        IPField("hostaddrv4", "0.0.0.0"),
        ShortField("servno", 0x00),
    ]


class SAPMSClient2(PacketNoPadded):
    """SAP Message Server Client packet version 2

    Packet that contains information about a client of the Message Server
    service. This packet is for version 2, which has been seen only on old
    releases (SAP NW 2004s).
    """
    name = "SAP Message Server Client version 2"
    fields_desc = [
        StrFixedLenField("client", None, 40),
        StrFixedLenField("host", None, 32),
        StrFixedLenField("service", None, 20),
        FlagsField("msgtype", 0, 8, ["ICM", "ATP", "UP2", "SPO", "BTC", "ENQ", "UPD", "DIA"]),
        IPField("hostaddrv4", "0.0.0.0"),
        ShortField("servno", 0x00),
        ByteEnumKeysField("status", 0x00, ms_client_status_values),
        ByteField("nitrace", 0x00),
        StrFixedLenField("padd", None, 14),
    ]


class SAPMSClient3(Packet):
    """SAP Message Server Client packet version 3

    Packet that contains information about a client of the Message Server
    service. This packet is for version 3.
    """
    name = "SAP Message Server Client version 3"
    fields_desc = [
        StrFixedLenField("client", None, 40),
        StrFixedLenField("host", None, 64),
        StrFixedLenField("service", None, 20),
        FlagsField("msgtype", 0, 8, ["ICM", "ATP", "UP2", "SPO", "BTC", "ENQ", "UPD", "DIA"]),
        IP6Field("hostaddrv6", "::1"),
        IPField("hostaddrv4", "0.0.0.0"),
        ShortField("servno", 0x00),
        ByteEnumKeysField("status", 0x00, ms_client_status_values),
        ByteField("nitrace", 0x00),
        ByteField("padd", 0),
    ]


class SAPMSClient4(PacketNoPadded):
    """SAP Message Server Client packet version 4

    Packet that contains information about a client of the Message Server
    service. This packet is for version 4.
    """
    name = "SAP Message Server Client version 4"
    fields_desc = [
        StrFixedLenField("client", None, 40),
        StrFixedLenField("host", None, 64),
        StrFixedLenField("service", None, 20),
        FlagsField("msgtype", 0, 8, ["ICM", "ATP", "UP2", "SPO", "BTC", "ENQ", "UPD", "DIA"]),
        IP6Field("hostaddrv6", "::1"),
        IPField("hostaddrv4", "0.0.0.0"),
        ShortField("servno", 0x00),
        ByteEnumKeysField("status", 0x00, ms_client_status_values),
        ByteField("nitrace", 0x00),
        IntField("sys_service", 0x00),
        StrFixedLenField("padd", None, 7),
    ]


class SAPMSStat3(PacketNoPadded):
    """SAP Message Server Statistics version 3

    Packet that contains statistics information of the Message Server service.
    This packet is for version 3.
    """
    # TODO: The fields on this packet are not correctly defined
    name = "SAP Message Server Statistics version 3"
    fields_desc = [
        ByteField("active", 0),
        ByteField("version", 0),
        ShortField("unused1", 0),
        IntField("no_requests", 0),
        StrFixedLenField("no_requests_padd", "", 12),
        IntField("no_error", 0),
        StrFixedLenField("no_error_padd", "", 4),
        IntField("no_login", 0),
        StrFixedLenField("no_login_padd", "", 4),
        IntField("no_logout", 0),
        StrFixedLenField("no_logout_padd", "", 4),
        IntField("no_send_by_name", 0),
        StrFixedLenField("no_send_by_name_padd", "", 4),
        IntField("no_send_by_type", 0),
        StrFixedLenField("no_send_by_type_padd", "", 4),
        IntField("no_adm_messages", 0),
        StrFixedLenField("no_adm_messages_padd", "", 4),
        IntField("no_adms", 0),
        StrFixedLenField("no_amds_padd", "", 4),
        StrFixedLenField("no_adm_type", "", 648),
        IntField("no_mod_types", 0),
        StrFixedLenField("no_mod_types_padd", "", 4),
        IntField("no_opcodes_rcvd", 0),
        StrFixedLenField("no_opcodes_rcvd_padd", "", 4),
        IntField("no_opcodes_send", 0),
        StrFixedLenField("no_opcodes_send_padd", "", 4),
        IntField("no_opcodes", 0),
        StrFixedLenField("no_opcode_type", "", 408),
        IntField("no_keepalive_send", 0),
        StrFixedLenField("no_keepalive_send_padd", "", 4),
        IntField("no_keepalive_rcvd", 0),
        StrFixedLenField("no_keepalive_rcvd_padd", "", 4),
        IntField("no_keepalive_disc", 0),
        StrFixedLenField("no_keepalive_disc_padd", "", 4),
        IntField("no_bytes_read", 0),
        StrFixedLenField("no_bytes_read_padd", "", 12),
        IntField("no_bytes_written", 0),
        StrFixedLenField("no_bytes_written_padd", "", 12),
        IntField("no_clients", 0),
        StrFixedLenField("sta_time", "", 30),
        StrFixedLenField("act_time", "", 30),
    ]


class SAPMSCounter(PacketNoPadded):
    """SAP Message Server Counter packet.

    Packet containing information about a Counter.
    """
    name = "SAP Message Server Counter"
    fields_desc = [
        StrFixedLenField("uuid", "", 40),
        IntField("count", 0),
        IntField("no", 0),
    ]


class SAPMSLogon(PacketNoPadded):
    """SAP Message Server Logon packet.

    Packet containing logon data.
    """
    name = "SAP Message Server Logon"
    fields_desc = [
        ShortEnumKeysField("type", 0, ms_logon_type_values),
        ShortField("port", 0),
        IPField("address", "0.0.0.0"),
        FieldLenField("logonname_length", None, length_of="logonname", fmt="!H"),  # <= 80h bytes
        StrLenField("logonname", "", length_from=lambda pkt:pkt.logonname_length),
        FieldLenField("prot_length", None, length_of="prot", fmt="!H"),  # <= 80h bytes
        StrLenField("prot", "", length_from=lambda pkt:pkt.prot_length),
        FieldLenField("host_length", None, length_of="host", fmt="!H"),  # <= 100h bytes
        StrLenField("host", "", length_from=lambda pkt:pkt.host_length),
        FieldLenField("misc_length", None, length_of="misc", fmt="!H"),  # <= 100h bytes
        StrLenField("misc", "", length_from=lambda pkt:pkt.misc_length),
        FieldLenField("address6_length", 16, length_of="address6", fmt="!h"),  # == 16 bytes
        ConditionalField(IP6Field("address6", "::"), lambda pkt:pkt.address6_length > 0),
        ConditionalField(SignedIntField("end", -1), lambda pkt:pkt.address6_length > 0),
    ]


class SAPMSProperty(Packet):
    """SAP Message Server Property packet.

    Packet containing information about properties.
    """
    name = "SAP Message Server Property"
    fields_desc = [
        StrNullFixedLenField("client", None, 40),
        IntEnumField("id", 0x00, ms_property_id_values),

        # MS_PROPERTY_VHOST
        ConditionalField(ShortEnumKeysField("logon", 0, ms_logon_type_values), lambda pkt:pkt.id in [0x02]),
        ConditionalField(StrFixedLenField("pad", None, 12), lambda pkt:pkt.id in [0x02]),
        ConditionalField(ShortField("len", 0), lambda pkt:pkt.id in [0x02]),
        ConditionalField(StrLenField("value", "", length_from=lambda pkt: pkt.len), lambda pkt:pkt.id in [0x02]),
        ConditionalField(ShortField("pad2", 0xffff), lambda pkt:pkt.id in [0x02]),

        # MS_PROPERTY_IPADR
        ConditionalField(IPField("address", "0.0.0.0"), lambda pkt:pkt.id in [0x03]),
        ConditionalField(IP6Field("address6", "::"), lambda pkt:pkt.id in [0x03]),

        # MS_PROPERTY_PARAM
        ConditionalField(FieldLenField("param_len", 0, length_of="param", fmt="I"), lambda pkt:pkt.id in [0x04]),
        ConditionalField(StrLenField("param", "", length_from=lambda pkt: pkt.param_len), lambda pkt:pkt.id in [0x04]),
        ConditionalField(StrLenField("param_padding", "", length_from=lambda pkt: 100 - pkt.param_len), lambda pkt:pkt.id in [0x04]),
        ConditionalField(ShortField("pad3", 0), lambda pkt:pkt.id in [0x04]),
        ConditionalField(FieldLenField("value_len", 0x0, length_of="value", fmt="H"), lambda pkt:pkt.id in [0x04]),
        ConditionalField(StrLenField("value", "", length_from=lambda pkt:pkt.value_len), lambda pkt:pkt.id in [0x04]),

        # MS_PROPERTY_SERVICE
        ConditionalField(ShortField("service", 0), lambda pkt:pkt.id in [0x05]),
        ConditionalField(ByteField("value", 0), lambda pkt:pkt.id in [0x05]),

        # Release Information fields
        ConditionalField(StrNullFixedLenField("release", "720", length=10), lambda pkt:pkt.id in [0x07]),
        ConditionalField(IntField("patchno", 0), lambda pkt:pkt.id in [0x07]),
        ConditionalField(IntField("supplvl", 0), lambda pkt:pkt.id in [0x07]),
        ConditionalField(IntField("platform", 0), lambda pkt:pkt.id in [0x07]),
    ]


class SAPMSJ2EECluster(Packet):
    """SAP Message Server J2EE Cluster packet

    This packet is used for the Message Server protocol for J2EE cluster nodes.
    """
    name = "SAP Message Server J2EE Cluster"
    cluster_no = 68199
    node_no = 5
    cluster_no_id = cluster_no + 100 + 50 + node_no
    icm_port = 5020

    fields_desc = [
        IntField("cluster_id", cluster_no_id),
        IntField("group_id", cluster_no),
        IntField("join_port", icm_port),
        StrFixedLenField("name", "J2EE{}".format(cluster_no_id), 32),
        StrFixedLenField("host", "localhost", 32),
        IPField("hostaddrv4", "127.0.0.1"),
        ByteField("type", 0x02),
        ByteField("state", 0x00),
        StrFixedLenField("service_mask", 32 * "\xff", 32),
        ByteField("version", 0x02),
        ByteField("modifiers", 0x02),
        StrFixedLenField("reserved", 4 * "\x00", 4),
        IP6Field("hostaddrv6", "::1")
    ]


class SAPMSJ2EEHeader(Packet):
    """SAP Message Server J2EE Header packet

    This packet is used for the Message Server protocol for J2EE nodes.
    """
    name = "SAP Message Server J2EE Header"
    cluster_no = 68199

    fields_desc = [
        IntField("sender_cluster_id", cluster_no),
        IntField("cluster_id", cluster_no),
        IntField("service_id", 9),
        IntField("group_id", 0),
        ByteField("node_type", 0x02),
        IntField("total_length", 0),
        IntField("current_length", 0),
        IntField("current_offset", 0),
        ByteField("total_blocks", 0),
        ByteField("current_block", 0),
        IntField("message_type", 0)
    ]


class SAPMSJ2EEService(PacketNoPadded):
    """SAP Message Server J2EE Service packet

    This packet is used to describe a J2EE service.
    """
    name = "SAP Message Server J2EE Service"
    fields_desc = [
        ByteField("service_id", 0x00),
        ByteField("attached_nodes", 0x00),
        StrFixedLenField("name", "\x00", 50),
    ]


class SAPDPInfo1(Packet):
    """SAP Dispatcher Info packet

    This packet is encapsulated inside SAPMS packet
    and before the MS ADM payload. Kernel 745
    """
    name = "SAP Dispatcher Info V1"
    fields_desc = [
        ByteEnumKeysField("dp_req_prio", 0x1, dp_prio_values),
        IntField("dp_user_trace", 0x0),
        IntField("dp_req_len", 0x0),

        ShortField("dp_padd3", 0x0),
        ByteField("dp_padd4", 0x0),
        ByteEnumKeysField("dp_type_from", 0x2, dp_type_values),
        StrFixedLenField("dp_fromname", " "*40, 40),
        ShortField("dp_padd41", 0x0),
        ByteField("dp_padd42", 0x0),
        ByteEnumKeysField("dp_agent_type_from", 0x6, dp_agent_type_values),
        ShortField("dp_padd43", 0x0),
        ByteField("dp_padd44", 0x0),
        ByteEnumKeysField("dp_worker_type_from", 0x1, dp_worker_type_values),
        IntField("dp_worker_from_num", 0x0),
        ShortField("dp_padd6", 0x0),
        ShortField("dp_padd7", 0x0),

        ByteField("dp_addr_from_t", 0xff),
        ShortField("dp_padd8", 0x0),
        ShortField("dp_addr_from_u", 0xffff),
        ByteField("dp_addr_from_m", 0xff),
        ByteField("dp_padd9", 0x1),
        IntField("dp_respid_from", 0x0),

        ShortField("dp_padd10", 0x0),
        ByteField("dp_padd11", 0x0),
        ByteEnumKeysField("dp_type_to", 0x2, dp_type_values),
        StrFixedLenField("dp_toname", " "*40, 40),

        ShortField("dp_padd51", 0x0),
        ByteField("dp_padd52", 0x0),
        ByteEnumKeysField("dp_agent_type_to", 0x6, dp_agent_type_values),
        ShortField("dp_padd54", 0x0),
        ByteField("dp_padd55", 0x0),
        ByteEnumKeysField("dp_worker_type_to", 0x1, dp_worker_type_values),

        IntField("dp_worker_to_num", 0x0),

        ShortField("dp_padd01", 0),
        ShortField("dp_padd02", 0),

        ByteField("dp_addr_to_t", 0xff),
        ShortField("dp_padd03", 0x1),
        ShortField("dp_addr_to_u", 0xffff),
        ByteField("dp_addr_to_m", 0x0),

        ByteField("dp_padd21", 0x0),
        IntField("dp_respid_to", 0),
        ByteField("dp_padd22", 0),
        ShortField("dp_padd23", 0),

        ByteEnumKeysField("dp_req_handler", 40, dp_req_handler_values),
        IntField("dp_req_rc", 0x0),

        StrFixedLenField("dp_blob_padding", None, 224),
        Field("dp_blob_56", 6, '<L'),
        Field("dp_blob_57", 1, '<L'),
        Field("dp_blob_worker_from_num", 0, '<L'),

        ByteField("dp_blob_worker_type_from", 0),
        StrFixedLenField("dp_blob_62", "", 3),

        Field("dp_blob_addr_from_t", 0, '<L'),
        Field("dp_blob_addr_from_u", 0, '<L'),

        ByteField("dp_blob_worker_type_to", 0),
        StrFixedLenField("dp_blob_63", "", 3),

        Field("dp_blob_respid_from", 0, '<L'),

        StrFixedLenField("dp_blob_64", "", 3),

        StrFixedLenField("dp_blob_dst", "", 80),
        ByteField("dp_blob_xx", 0),
        StrFixedLenField("dp_blob_yy", "", 8),
    ]


class SAPDPInfo2(Packet):
    """SAP Dispatcher Info packet

    This packet is encapsulated inside SAPMS packet
    and before the MS ADM payload. Kernel 720.
    """
    name = "SAP Dispatcher Info v2"
    fields_desc = [
        ByteEnumKeysField("dp_req_prio", 0x1, dp_prio_values),
        XByteField("dp_blob_00", 0x2),
        XByteField("dp_blob_01", 0x80),
        XByteField("dp_blob_02", 0x21),
        ShortField("dp_blob_03", 0x0),
        ShortField("dp_blob_04", 0xffff),
        StrFixedLenField("dp_blob_05", "\xff\xff\xff\xff\xff", 5),

        ByteField("dp_addr_from_t", 0x0),

        StrFixedLenField("dp_blob_06", "\xff\xff", 2),
        StrFixedLenField("dp_blob_07", "\xff\xff\xff\xff", 4),
        StrFixedLenField("dp_blob_08", "\xff\xff\xff\xff", 4),
        StrFixedLenField("dp_blob_09", "\xff\xcc", 2),
        StrFixedLenField("dp_blob_10", "\x01\x00", 2),
        ByteField("dp_addr_from_m", 0x0),
        ByteField("dp_addr_from_u", 0x0),
        StrFixedLenField("dp_blob_11", "\xff\xff", 2),
        StrFixedLenField("dp_blob_12", "\xff\xff\xff\xff", 4),
        StrFixedLenField("dp_blob_13", "", 86),
        StrFixedLenField("dp_blob_14", "", 5),

        StrFixedLenField("dp_name_to", "", 40),

        XByteField("dp_blob_15", 0x0),
        ByteField("dp_addr_to_t", 0x0),
        ShortField("dp_addr_to_u", 0x0),
        ByteField("dp_addr_to_m", 0x0),
        ByteField("dp_blob_16", 0x0),
        ShortField("dp_respid_to", 0x0),

        StrFixedLenField("dp_blob_17", "\xff\xff\xff\xff", 4),
        StrFixedLenField("dp_blob_18", "\x00\x00\x00\x00", 4),
        Field("dp_blob_19", 0x1, '<L'),
        StrFixedLenField("dp_blob_20", "", 12),
        Field("dp_blob_21", 0x0, '<L'),
    ]


class SAPDPInfo3(Packet):
    """SAP Dispatcher Info packet

    This packet is encapsulated inside SAPMS packet
    and before the MS ADM payload. Kernel 749.
    """
    name = "SAP Dispatcher Info v3"
    fields_desc = [
        IntField("dp_padd1", 185),

        ByteEnumKeysField("dp_req_prio", 0x1, dp_prio_values),
        ShortField("dp_padd2", 0x0),
        ByteField("dp_padd3", 0x0),

        ByteField("dp_padd4", 0x0),
        IntField("dp_req_len", 0x0),
        ShortField("dp_padd5", 0x0),
        ByteField("dp_padd6", 0x0),
        ByteEnumKeysField("dp_type_from", 0x2, dp_type_values),
        StrFixedLenField("dp_fromname", " "*40, 40),
        ShortField("dp_padd7", 0x0),
        ByteField("dp_padd8", 0x0),
        ByteEnumKeysField("dp_agent_type_from", 0x6, dp_agent_type_values),
        ShortField("dp_padd9", 0x0),
        ByteField("dp_padd10", 0x0),

        ByteField("dp_padd12", 0xff),
        ShortField("dp_padd13", 0x0),
        ByteEnumKeysField("dp_worker_type_from", 0x1, dp_worker_type_values),

        ByteField("dp_worker_from_num", 0x0),
        ByteField("dp_padd133", 0x0),
        ShortField("dp_padd111", 0x0000),
        ByteField("dp_padd11", 0x00),

        ByteField("dp_addr_from_t", 0x0),
        ShortField("dp_padd14", 0x0),
        ShortField("dp_addr_from_u", 0x0),
        ByteField("dp_addr_from_m", 0x0),
        ByteField("dp_padd15", 0x1),
        IntField("dp_respid_from", 0x0),

        ShortField("dp_padd16", 0x0),
        ByteField("dp_padd17", 0x0),
        ByteEnumKeysField("dp_type_to", 0x2, dp_type_values),
        StrFixedLenField("dp_toname", " "*40, 40),

        ShortField("dp_padd18", 0x0),
        ByteField("dp_padd19", 0x0),
        ByteEnumKeysField("dp_agent_type_to", 0x6, dp_agent_type_values),

        ShortField("dp_padd20", 0x0),
        ByteField("dp_padd21", 0x0),

        ByteEnumKeysField("dp_worker_type_to", 0x1, dp_worker_type_values),
        ShortField("dp_padd22", 0x0),
        ByteField("dp_worker_to_num", 0x0),
        ByteField("dp_padd222", 0x0),

        IntField("dp_padd23", 0x0),

        ByteField("dp_addr_to_t", 0x0),
        ShortField("dp_padd24", 0x0),
        ShortField("dp_addr_to_u", 0x0),
        ByteField("dp_addr_from_m", 0x0),
        ByteField("dp_padd25", 0x1),

        IntField("dp_respid_to", 0x0),
        ShortField("dp_padd26", 0x0),
        ByteField("dp_padd27", 0x0),

        ByteEnumKeysField("dp_req_handler", 40, dp_req_handler_values),
        StrFixedLenField("dp_padd28", "\xff\xff\xff\xff", 4),

        IntField("dp_padd29", 0x0),
        IntField("dp_padd30", 0x0),
        IntField("dp_padd31", 0x0),

        StrFixedLenField("dp_padd32", "\x00"*5, 5),
    ]


class SAPMS(Packet):
    """SAP Message Server packet

    This packet is used for the Message Server protocol.
    """
    name = "SAP Message Server"
    fields_desc = [
        StrFixedLenField("eyecatcher", "**MESSAGE**\x00", 12),
        ByteField("version", 0x04),
        ByteEnumKeysField("errorno", 0x00, ms_errorno_values),
        StrFixedLenField("toname", "-" + " " * 39, 40),
        FlagsField("msgtype", 0, 8, ["DIA", "UPD", "ENQ", "BTC", "SPO", "UP2", "ATP", "ICM"]),
        ByteField("reserved", 0x00),
        ByteEnumKeysField("domain", 0x00, ms_domain_values),
        ByteField("reserved", 0x00),
        StrFixedLenField("key", "\x00" * 8, 8),
        ByteEnumKeysField("flag", 0x01, ms_flag_values),
        ByteEnumKeysField("iflag", 0x01, ms_iflag_values),
        StrFixedLenField("fromname", "-" + " " * 39, 40),
        ConditionalField(ShortField("diag_port", 3200), lambda pkt:pkt.iflag == 0x08 and pkt.flag == 0x02),  # for MS_REQUEST+MS_LOGIN_2 it's the diag port
        ConditionalField(ShortField("padd", 0x0000), lambda pkt:pkt.iflag != 0x08 or pkt.flag != 0x02),

        # OpCode fields
        ConditionalField(ByteEnumKeysField("opcode", 0x01, ms_opcode_values), lambda pkt:pkt.iflag in [0x00, 0x01, 0x02, 0x07]),  # extending all those fields with MS_SEND_TYPE and MS_SEND_TYPE_ONCE packets
        ConditionalField(ByteEnumKeysField("opcode_error", 0x00, ms_opcode_error_values), lambda pkt:pkt.iflag in [0x00, 0x01, 0x02, 0x7]),
        ConditionalField(ByteField("opcode_version", 0x01), lambda pkt:pkt.iflag in [0x00, 0x01, 0x02, 0x07]),
        ConditionalField(ByteField("opcode_charset", 0x03), lambda pkt:pkt.iflag in [0x00, 0x01, 0x02, 0x07]),
        ConditionalField(StrField("opcode_value", ""), lambda pkt:pkt.iflag in [0x00, 0x01] and pkt.opcode not in [0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0a, 0x11, 0x1c, 0x22, 0x23, 0x24, 0x25, 0x26, 0x27, 0x28, 0x29, 0x2a, 0x2b, 0x2c, 0x2d, 0x2f, 0x43, 0x44, 0x45, 0x46, 0x47, 0x4a]),
        ConditionalField(StrField("opcode_trailer", ""), lambda pkt:pkt.iflag in [0x00, 0x01] and pkt.opcode not in [0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0a, 0x11, 0x1c, 0x1e, 0x22, 0x23, 0x24, 0x25, 0x26, 0x27, 0x28, 0x29, 0x2a, 0x2b, 0x2c, 0x2d, 0x2f, 0x43, 0x44, 0x45, 0x46, 0x47, 0x4a]),

        # Dispatcher info
        ConditionalField(ByteField("dp_version", 0x0), lambda pkt:pkt.opcode == 0x0 or (pkt.opcode_version == 0x00 and pkt.opcode_charset == 0x00)),
        ConditionalField(PacketLenField("dp_info1", SAPDPInfo1(), SAPDPInfo1, length_from=lambda x: 507), lambda pkt:(pkt.opcode == 0x0 or (pkt.opcode_version == 0x00 and pkt.opcode_charset == 0x00)) and pkt.dp_version == 0x0d),  # 745 kernel

        ConditionalField(PacketLenField("dp_info2", SAPDPInfo2(), SAPDPInfo2, length_from=lambda x: 203), lambda pkt:(pkt.opcode == 0x0 or (pkt.opcode_version == 0x00 and pkt.opcode_charset == 0x00)) and pkt.dp_version == 0x0b),  # 720 kernel

        ConditionalField(PacketLenField("dp_info3", SAPDPInfo3(), SAPDPInfo3, length_from=lambda x: 179), lambda pkt:(pkt.opcode == 0x0 or (pkt.opcode_version == 0x00 and pkt.opcode_charset == 0x00)) and pkt.dp_version == 0x0e),  # 749 kernel

        # MS ADM layer
        ConditionalField(StrFixedLenField("adm_eyecatcher", "AD-EYECATCH\x00", 12), lambda pkt: pkt.iflag in [0x00, 0x02, 0x05, 0x07] or pkt.opcode == 0x0),
        ConditionalField(ByteField("adm_version", 0x01), lambda pkt:pkt.iflag in [0x00, 0x02, 0x05, 0x07] or pkt.opcode == 0x0),
        ConditionalField(ByteEnumKeysField("adm_type", 0x01, ms_adm_type_values), lambda pkt:pkt.iflag in [0x00, 0x02, 0x05, 0x07] or pkt.opcode == 0x0),
        ConditionalField(IntToStrField("adm_recsize", 104, 11), lambda pkt:pkt.iflag in [0x00, 0x02, 0x05, 0x07] or pkt.opcode == 0x0),
        ConditionalField(IntToStrField("adm_recno", 1, 11), lambda pkt:pkt.iflag in [0x00, 0x02, 0x05, 0x07] or pkt.opcode == 0x0),
        ConditionalField(PacketListField("adm_records", None, SAPMSAdmRecord), lambda pkt:pkt.iflag in [0x00, 0x02, 0x05, 0x07] or pkt.opcode == 0x0),

        # Server List fields
        ConditionalField(PacketListField("clients", None, SAPMSClient1), lambda pkt:pkt.opcode in [0x02, 0x03, 0x04, 0x05] and pkt.opcode_version == 0x01),
        ConditionalField(PacketListField("clients", None, SAPMSClient2), lambda pkt:pkt.opcode in [0x02, 0x03, 0x04, 0x05] and pkt.opcode_version == 0x02),
        ConditionalField(PacketListField("clients", None, SAPMSClient3), lambda pkt:pkt.opcode in [0x02, 0x03, 0x04, 0x05] and pkt.opcode_version == 0x03),
        ConditionalField(PacketListField("clients", None, SAPMSClient4), lambda pkt:pkt.opcode in [0x02, 0x03, 0x04, 0x05] and pkt.opcode_version == 0x04),

        # Change IP fields
        ConditionalField(IPField("change_ip_addressv4", "0.0.0.0"), lambda pkt:pkt.opcode == 0x06),
        ConditionalField(IP6Field("change_ip_addressv6", "::"), lambda pkt:pkt.opcode == 0x06 and pkt.opcode_version == 0x02),

        # Get/Set Text fields
        ConditionalField(StrFixedLenField("text_name", "", 40), lambda pkt:pkt.opcode in [0x22, 0x23]),
        ConditionalField(FieldLenField("text_length", None, length_of="text_value", fmt="!I"), lambda pkt:pkt.opcode in [0x22, 0x23]),
        ConditionalField(StrFixedLenField("text_value", "", length_from=lambda pkt:pkt.text_length or 80), lambda pkt:pkt.opcode in [0x22, 0x23]),

        # Counter fields
        ConditionalField(PacketField("counter", None, SAPMSCounter), lambda pkt:pkt.opcode in [0x24, 0x25, 0x26, 0x27, 0x28, 0x29]),
        ConditionalField(PacketListField("counters", None, SAPMSCounter), lambda pkt:pkt.opcode in [0x2a]),

        # Security Key 1 fields
        ConditionalField(StrFixedLenField("security_name", None, 40), lambda pkt:pkt.opcode in [0x07, 0x08]),
        ConditionalField(StrFixedLenField("security_key", None, 256), lambda pkt:pkt.opcode in [0x07, 0x08]),

        # Security Key 2 fields
        ConditionalField(IPField("security2_addressv4", "0.0.0.0"), lambda pkt:pkt.opcode == 0x09),
        ConditionalField(ShortField("security2_port", 0), lambda pkt:pkt.opcode == 0x09),
        ConditionalField(StrFixedLenField("security2_key", None, 256), lambda pkt:pkt.opcode == 0x09),
        ConditionalField(IP6Field("security2_addressv6", "::"), lambda pkt:pkt.opcode == 0x09),

        # Hardware ID field
        ConditionalField(StrNullFixedLenField("hwid", "", length=99), lambda pkt:pkt.opcode == 0x0a),

        # Statistics
        ConditionalField(PacketField("stats", None, SAPMSStat3), lambda pkt:pkt.opcode == 0x11 and pkt.flag == 0x03),

        # Codepage
        ConditionalField(IntField("codepage", 0), lambda pkt:pkt.opcode == 0x1c and pkt.flag == 0x03),

        # Dump Info Request fields
        ConditionalField(ByteField("dump_dest", 0x02), lambda pkt:pkt.opcode == 0x1E and pkt.flag == 0x02),
        ConditionalField(StrFixedLenField("dump_filler", "\x00\x00\x00", 3), lambda pkt:pkt.opcode == 0x1E and pkt.flag == 0x02),
        ConditionalField(ShortField("dump_index", 0x00), lambda pkt:pkt.opcode == 0x1E and pkt.flag == 0x02),
        ConditionalField(ShortEnumKeysField("dump_command", 0x01, ms_dump_command_values), lambda pkt:pkt.opcode == 0x1E and pkt.flag == 0x02),
        ConditionalField(StrFixedLenField("dump_name", "\x00" * 40, 40), lambda pkt:pkt.opcode == 0x1E and pkt.flag == 0x02),

        # File Reload fields
        ConditionalField(ByteEnumKeysField("file_reload", 0, ms_file_reload_values), lambda pkt:pkt.opcode == 0x1f),
        ConditionalField(StrFixedLenField("file_padding", "\x00\x00", 2), lambda pkt:pkt.opcode == 0x1f),

        # Get/Set/Del Logon fields
        ConditionalField(PacketField("logon", None, SAPMSLogon), lambda pkt:pkt.opcode in [0x2b, 0x2c, 0x2d]),

        # Server Disconnect/Shutdown fields
        ConditionalField(PacketField("shutdown_client", None, SAPMSClient3), lambda pkt:pkt.opcode in [0x2e, 0x2f, 0x30, 0x4a]),
        ConditionalField(FieldLenField("shutdown_reason_length", None, length_of="shutdown_reason", fmt="!H"), lambda pkt:pkt.opcode in [0x2e, 0x2f, 0x30, 0x4a]),
        ConditionalField(StrLenField("shutdown_reason", "", length_from=lambda pkt:pkt.shutdown_reason_length), lambda pkt:pkt.opcode in [0x2e, 0x2f, 0x30, 0x4a]),

        # Get/Set Property fields
        ConditionalField(PacketField("property", None, SAPMSProperty), lambda pkt:pkt.opcode in [0x43, 0x44, 0x45]),

        # IP/Port to name fields
        ConditionalField(IPField("ip_to_name_address4", "0.0.0.0"), lambda pkt:pkt.opcode == 0x46 and pkt.opcode_version == 0x01),
        ConditionalField(IP6Field("ip_to_name_address6", "::"), lambda pkt:pkt.opcode == 0x46 and pkt.opcode_version == 0x02),
        ConditionalField(ShortField("ip_to_name_port", 0), lambda pkt:pkt.opcode == 0x46),
        ConditionalField(FieldLenField("ip_to_name_length", None, length_of="ip_to_name", fmt="!I"), lambda pkt:pkt.opcode == 0x46),
        ConditionalField(StrLenField("ip_to_name", "", length_from=lambda pkt:pkt.logonname_length), lambda pkt:pkt.opcode == 0x46),

        # Check ACL fields
        ConditionalField(ShortField("error_code", 0), lambda pkt:pkt.opcode == 0x47),
        ConditionalField(StrFixedLenField("acl", "", 46), lambda pkt:pkt.opcode == 0x47),
    ]


# Bind SAP NI with the MS ports (both internal & external)
bind_layers(TCP, SAPNI, dport=3600)
bind_layers(TCP, SAPNI, dport=3900)
