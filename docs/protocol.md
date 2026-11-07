# Buds3 Pro protocol notes

Frame: `FD | size(2, LE) | msg_id | payload | crc16(2, LE) | DD`
- `size = 1 + len(payload) + 2`; bit 12 of the size word marks a response.
- CRC16-CCITT (XModem, poly 0x1021, init 0) over `msg_id + payload`.

RFCOMM channels observed on Windows: 20 and 27 answer with Samsung frames; 27 accepts head-tracking.
