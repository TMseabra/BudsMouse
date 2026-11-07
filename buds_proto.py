"""Minimal Galaxy Buds SPP protocol helpers (framing, CRC16, spatial audio).

Frame (Buds3 Pro, non-legacy header):
    FD | size(2, LE; bit12 = response) | msg_id | payload | crc16(2, LE) | DD
    size = 1 + len(payload) + 2 ; CRC16-CCITT (XModem) over msg_id + payload.
Protocol details taken from GalaxyBudsClient (timschneeb).
"""
import socket
import struct

SOM, EOM = 0xFD, 0xDD

MSG_SET_SPATIAL_AUDIO = 124
MSG_SPATIAL_AUDIO_DATA = 194
MSG_SPATIAL_AUDIO_CONTROL = 195

CTRL_ATTACH, CTRL_DETACH, CTRL_KEEPALIVE = 0, 1, 4  # SPATIAL_AUDIO_CONTROL payloads
KEEPALIVE_SECONDS = 2  # buds drop head-tracking without periodic keep-alives
DATA_GRV = 32


def crc16(data: bytes) -> int:
    crc = 0
    for b in data:
        crc ^= b << 8
        for _ in range(8):
            crc = ((crc << 1) ^ 0x1021) if crc & 0x8000 else (crc << 1)
            crc &= 0xFFFF
    return crc


def build(msg_id: int, payload: bytes = b"") -> bytes:
    size = 1 + len(payload) + 2
    body = bytes([msg_id]) + payload
    return bytes([SOM]) + struct.pack("<H", size) + body + struct.pack("<H", crc16(body)) + bytes([EOM])


class Parser:
    """Accumulates raw bytes and yields (msg_id, payload, crc_ok)."""

    def __init__(self):
        self.buf = bytearray()

    def feed(self, data: bytes):
        self.buf += data
        while True:
            i = self.buf.find(SOM)
            if i < 0:
                self.buf.clear()
                return
            del self.buf[:i]
            if len(self.buf) < 4:
                return
            size = struct.unpack_from("<H", self.buf, 1)[0] & 0x3FF
            total = 1 + 2 + size + 1
            if len(self.buf) < total:
                return
            frame = bytes(self.buf[:total])
            del self.buf[:total]
            if frame[-1] != EOM:
                continue
            body = frame[3:3 + size - 2]
            crc = struct.unpack_from("<H", frame, 3 + size - 2)[0]
            yield body[0], body[1:], crc == crc16(body)


def connect(mac: str, channel: int, timeout: float = 5) -> socket.socket:
    s = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
    s.settimeout(timeout)
    s.connect((mac, channel))
    return s


def decode_grv(payload: bytes):
    """SPATIAL_AUDIO_DATA / BudGrv -> (w, x, y, z) quaternion or None."""
    if len(payload) < 10 or payload[0] != DATA_GRV:
        return None
    return tuple(v / 10000.0 for v in struct.unpack_from("<4h", payload, 1))
