#cython: embedsignature=True
cimport cython
from libcpp.string cimport string
from libc.stdint cimport uint16_t

import re

import numpy as np


ctypedef unsigned char uchar
ctypedef uint16_t crc_t


@cython.internal
cdef class _Flags:
    cdef:
        readonly string START

    def __cinit__(self):
        self.START = '|||'


@cython.internal
cdef class _PacketTypes:
    cdef:
        readonly int NONE
        readonly int ACK
        readonly int NACK
        readonly int DATA

    def __cinit__(self):
        self.NONE = PACKET_TYPE_NONE
        self.ACK = PACKET_TYPE_ACK
        self.NACK = PACKET_TYPE_NACK
        self.DATA = PACKET_TYPE_DATA


PACKET_TYPES = _PacketTypes()
FLAGS = _Flags()


cdef extern from "PacketParser.h":
    cdef enum packet_type "Packet::packet_type::EnumType":
        PACKET_TYPE_NONE "Packet::packet_type::NONE"
        PACKET_TYPE_ACK "Packet::packet_type::ACK"
        PACKET_TYPE_NACK "Packet::packet_type::NACK"
        PACKET_TYPE_DATA "Packet::packet_type::DATA"

    cdef cppclass Packet:
        uint16_t iuid_
        packet_type type_
        uint16_t payload_length_
        uint16_t buffer_size_
        uchar *payload_buffer_
        uint16_t crc_

        Packet()
        string data() except +
        uchar type()
        void type(uchar command_with_type_msb)

    cdef cppclass PacketParser:
        int payload_bytes_received_
        int payload_bytes_expected_
        bint message_completed_
        bint parse_error_
        uint16_t crc_

        PacketParser()
        void parse_byte(uchar *byte)
        void reset(Packet *packet)


cdef extern from "crc-16.h":
    crc_t c_crc_init "crc_init" ()
    crc_t c_crc_finalize "crc_finalize" (crc_t crc)
    crc_t c_crc_update "crc_update" (crc_t crc, uchar *data, size_t data_len)
    crc_t c_crc_update_byte "crc_update_byte" (crc_t crc, uchar data)


cdef class cPacket:
    cdef Packet *thisptr

    def __cinit__(self):
        self.thisptr = new Packet()

    def data(self):
        return self.thisptr.data()

    def __dealloc__(self):
        del self.thisptr

    def data_ptr(self):
        return <size_t>self.thisptr.payload_buffer_

    property crc:
        def __get__(self):
            return self.thisptr.crc_

    property type_:
        def __get__(self):
            return self.thisptr.type()
        def __set__(self, value):
            self.thisptr.type(value)

    property iuid:
        def __get__(self):
            return self.thisptr.iuid_
        def __set__(self, value):
            self.thisptr.iuid_ = value


cdef class cPacketParser:
    cdef PacketParser *thisptr

    def __cinit__(self):
        self.thisptr = new PacketParser()

    def __dealloc__(self):
        del self.thisptr

    def parse(self, uchar [:] packet_buffer):
        packet = cPacket()
        self.thisptr.reset(packet.thisptr)
        cdef int i
        for i in xrange(len(packet_buffer)):
            self.thisptr.parse_byte(<uchar *>&packet_buffer[i])
            error = self.thisptr.parse_error_
            if error:
                self.thisptr.reset(packet.thisptr)
                raise RuntimeError, ('Error parsing packet: %s' %
                                     np.asarray(packet_buffer).tostring())
        return packet

    property crc:
        def __get__(self):
            return self.thisptr.crc_


def crc_init():
    return c_crc_init()


def crc_finalize(crc):
    return c_crc_finalize(crc)


def crc_update(uint16_t crc, uchar [:] data):
    return c_crc_update(crc, &data[0], len(data))


def crc_update_byte(uint16_t crc, uchar octet):
    return c_crc_update_byte(crc, octet)


def compute_crc16(data):
    cdef string data_ = data
    cdef uint16_t crc = crc_init()
    crc = c_crc_update(crc, <uchar *>data_.c_str(), len(data))
    return crc_finalize(crc)


def byte_pair(value):
    return (chr((value >> 8) & 0x0FF), chr(value & 0x0FF))


def create_ack_packet_bytes(interface_unique_id):
    iuid = byte_pair(interface_unique_id)

    packet_str = '%s%s%s' % (iuid[0], iuid[1], chr(PACKET_TYPES.ACK))

    return np.fromstring(FLAGS.START + packet_str, dtype='uint8')


def create_nack_packet_bytes(interface_unique_id, max_packet_length=0):
    iuid = byte_pair(interface_unique_id)
    packet_str = '%s%s%s%s' % (iuid[0], iuid[1], chr(PACKET_TYPES.NACK),
                               chr(max_packet_length))

    return np.fromstring(FLAGS.START + packet_str, dtype='uint8')


def create_data_packet_bytes(interface_unique_id, payload):
    iuid = byte_pair(interface_unique_id)

    crc = compute_crc16(payload)
    packet_str = '%s%s%s%s%s%s%s' % (iuid[0], iuid[1], chr(PACKET_TYPES.DATA),
                                     chr(len(payload)), payload,
                                     chr((crc >> 8) & 0x0FF), chr(crc & 0x0FF))

    return np.fromstring(FLAGS.START + packet_str, dtype='uint8')


PACKET_NAME_BY_TYPE = {PACKET_TYPE_NONE: 'NONE',
                       PACKET_TYPE_ACK: 'ACK',
                       PACKET_TYPE_NACK: 'NACK',
                       PACKET_TYPE_DATA: 'DATA'}
