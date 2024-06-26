# coding: utf-8
from nose.tools import eq_, ok_
from nadamq.NadaMq import cPacket, PACKET_TYPES


def test_buffer_auto():
    """
    Test auto-buffer based on data content.
    """
    p = cPacket(iuid=1234, type_=PACKET_TYPES.DATA, data=b'hello, world!')
    eq_(p.buffer_size, len(b'hello, world!'))
    eq_(p.data(), b'hello, world!')


def test_buffer_larger_than_data():
    """
    Test setting data while allocating larger buffer.
    """
    p = cPacket(iuid=1234, type_=PACKET_TYPES.DATA, data=b'hello, world!',
                buffer_size=1024)
    eq_(p.data(), b'hello, world!')
    eq_(p.buffer_size, 1024)


def test_buffer():
    """
    Test setting allocating buffer without setting data contents.
    """
    p = cPacket(iuid=1234, type_=PACKET_TYPES.DATA, buffer_size=1024)
    eq_(p.buffer_size, 1024)
    eq_(p.data(), b'')


def test_no_buffer():
    """
    Test no buffer allocation.
    """
    p = cPacket(iuid=1234, type_=PACKET_TYPES.DATA)
    try:
        p.data()
    except RuntimeError as e:
        ok_('No buffer has been set/allocated.' in str(e))


def test_default_packet():
    """
    Test default packet allocation, i.e., no iuid, type, or data/buffer.
    """
    p = cPacket()
    eq_(p.iuid, 0)
    eq_(p.type_, PACKET_TYPES.NONE)
    eq_(p.buffer_size, 0)


def test_cPacket():
    """
    Test serialization of ``cPacket`` containing ``"hello, world!"``.
    """
    packet = cPacket(data=b'hello, world!', type_=PACKET_TYPES.DATA)
    eq_(packet.tobytes(), b'|||\x00\x00d\x00\rhello, world!\xfa5')
