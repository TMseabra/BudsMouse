"""Phase 1b - probe RFCOMM channels on the Buds and log raw traffic.

Tip: on the Buds3 Pro, channels 20 and 27 speak the Samsung protocol (27 for head-tracking).

Windows needs an explicit RFCOMM channel number, so this tries channels
1..30 until one connects, then hex-dumps everything received into a log file.

Usage:
    python phase1_rfcomm.py AA:BB:CC:DD:EE:FF            # probe + listen
    python phase1_rfcomm.py AA:BB:CC:DD:EE:FF --channel 5
"""
import argparse
import socket
import time
from datetime import datetime


def connect(mac, channel, timeout=4):
    s = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
    s.settimeout(timeout)
    s.connect((mac, channel))
    return s


def probe(mac, channels):
    for ch in channels:
        try:
            s = connect(mac, ch)
            print(f"[+] channel {ch}: connected")
            return s, ch
        except OSError as e:
            print(f"[-] channel {ch}: {e}")
    return None, None


def listen(s, logfile):
    s.settimeout(1)
    print("Listening (Ctrl+C to stop). Move/open/close the case; raw frames below.")
    with open(logfile, "a", encoding="utf-8") as log:
        while True:
            try:
                data = s.recv(1024)
            except socket.timeout:
                continue
            if not data:
                print("[!] connection closed by the Buds")
                return
            line = f"{datetime.now().isoformat(timespec='milliseconds')} {data.hex(' ')}"
            print(line)
            log.write(line + "\n")
            log.flush()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mac")
    ap.add_argument("--channel", type=int)
    ap.add_argument("--log", default=f"rfcomm_{int(time.time())}.log")
    args = ap.parse_args()

    channels = [args.channel] if args.channel else range(1, 31)
    s, ch = probe(args.mac, channels)
    if not s:
        print("No RFCOMM channel accepted. Make sure the Buds are paired, out of the "
              "case (or case open) and not held by the phone / Galaxy Wearable.")
        return
    try:
        listen(s, args.log)
    except KeyboardInterrupt:
        pass
    finally:
        s.close()
        print(f"Log saved to {args.log}")


if __name__ == "__main__":
    main()
