"""Phase 2 - enable head-tracking on the Buds and print the sensor stream.

Usage:
    python phase2_sensors.py 2C:DA:46:8A:4D:A2 --channel 20
    python phase2_sensors.py MAC --seconds 30 --log sensors.log
See docs/testing.md for the test order (outside, case open, case closed).
"""
import argparse
import socket
import time  # keep-alive timing

import buds_proto as bp


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mac")
    ap.add_argument("--channel", type=int, default=27)
    ap.add_argument("--seconds", type=float, default=20)
    ap.add_argument("--log")
    args = ap.parse_args()

    s = bp.connect(args.mac, args.channel)
    s.settimeout(0.5)
    print(f"connected on channel {args.channel}")
    log = open(args.log, "a", encoding="utf-8") if args.log else None

    s.send(bp.build(bp.MSG_SET_SPATIAL_AUDIO, bytes([1])))
    s.send(bp.build(bp.MSG_SPATIAL_AUDIO_CONTROL, bytes([bp.CTRL_ATTACH])))

    parser = bp.Parser()
    end = time.time() + args.seconds
    last_ka = time.time()
    counts = {}
    try:
        while time.time() < end:
            if time.time() - last_ka > bp.KEEPALIVE_SECONDS:
                s.send(bp.build(bp.MSG_SPATIAL_AUDIO_CONTROL, bytes([bp.CTRL_KEEPALIVE])))
                last_ka = time.time()
            try:
                data = s.recv(1024)
            except socket.timeout:
                continue
            if not data:
                print("[!] connection closed by the Buds")
                break
            for mid, payload, ok in parser.feed(data):
                counts[mid] = counts.get(mid, 0) + 1
                if mid == bp.MSG_SPATIAL_AUDIO_DATA:
                    q = bp.decode_grv(payload)
                    line = (f"GRV w={q[0]:+.3f} x={q[1]:+.3f} y={q[2]:+.3f} z={q[3]:+.3f}"
                            if q else f"SPATIAL_DATA event={payload[:1].hex()} {payload.hex(' ')}")
                elif mid == bp.MSG_SPATIAL_AUDIO_CONTROL:
                    line = f"SPATIAL_CONTROL {payload.hex(' ')}"
                else:
                    line = f"msg {mid} {payload.hex(' ')}"
                if not ok:
                    line += "  (bad crc)"
                if mid != 97 and mid != 96 or log:  # hide noisy status updates on console
                    print(line)
                if log:
                    log.write(f"{time.time():.3f} {line}\n")
    except KeyboardInterrupt:
        pass
    finally:
        try:
            s.send(bp.build(bp.MSG_SPATIAL_AUDIO_CONTROL, bytes([bp.CTRL_DETACH])))
            s.send(bp.build(bp.MSG_SET_SPATIAL_AUDIO, bytes([0])))
        except OSError:
            pass
        s.close()
        print("message counts by id:", counts)


if __name__ == "__main__":
    main()
