"""Phase 3 - move the Windows cursor with the Buds' motion.

Uses the *relative* rotation between consecutive quaternions, so no absolute
calibration is needed: rotating the buds about one axis moves the cursor
horizontally, about another vertically. Axis mapping/inversion are CLI flags
because the sensor frame inside the case is not known yet.

Usage:
    python phase3_mouse.py MAC --dry-run          # print dx,dy only
    python phase3_mouse.py MAC --sens 900 --invert-x
    python phase3_mouse.py MAC --x-axis 2 --y-axis 1   # axes: 0=x 1=y 2=z of rotation vector
Stop with Ctrl+C. Slam the real mouse into a corner? Not needed - just Ctrl+C.
"""
import argparse
import ctypes
import math
import socket
import time

import buds_proto as bp

MOUSEEVENTF_MOVE = 0x0001


def move(dx: int, dy: int):
    if dx or dy:
        ctypes.windll.user32.mouse_event(MOUSEEVENTF_MOVE, dx, dy, 0, 0)


def qmul(a, b):
    aw, ax, ay, az = a
    bw, bx, by, bz = b
    return (aw * bw - ax * bx - ay * by - az * bz,
            aw * bx + ax * bw + ay * bz - az * by,
            aw * by - ax * bz + ay * bw + az * bx,
            aw * bz + ax * by - ay * bx + az * bw)


def qconj(q):
    return (q[0], -q[1], -q[2], -q[3])


def qnorm(q):
    n = math.sqrt(sum(c * c for c in q)) or 1.0
    return tuple(c / n for c in q)


def rotvec(q):
    """Quaternion -> rotation vector (radians)."""
    w, x, y, z = q
    if w < 0:
        w, x, y, z = -w, -x, -y, -z
    s = math.sqrt(x * x + y * y + z * z)
    if s < 1e-9:
        return (0.0, 0.0, 0.0)
    ang = 2 * math.atan2(s, w)
    return (x / s * ang, y / s * ang, z / s * ang)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mac")
    ap.add_argument("--channel", type=int, default=27)
    ap.add_argument("--sens", type=float, default=800, help="pixels per radian")
    ap.add_argument("--smooth", type=float, default=0.5, help="0=none .. 0.95=heavy")
    ap.add_argument("--deadzone", type=float, default=0.002, help="radians/sample ignored")
    ap.add_argument("--x-axis", type=int, default=2, choices=[0, 1, 2])
    ap.add_argument("--y-axis", type=int, default=1, choices=[0, 1, 2])
    ap.add_argument("--invert-x", action="store_true")
    ap.add_argument("--invert-y", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    sx = -1 if args.invert_x else 1
    sy = -1 if args.invert_y else 1

    s = bp.connect(args.mac, args.channel)
    s.settimeout(0.5)
    s.send(bp.build(bp.MSG_SET_SPATIAL_AUDIO, bytes([1])))
    s.send(bp.build(bp.MSG_SPATIAL_AUDIO_CONTROL, bytes([bp.CTRL_ATTACH])))
    print("streaming - move the buds. Ctrl+C to stop.")

    parser = bp.Parser()
    prev = None
    fx = fy = 0.0   # smoothed velocity
    rx = ry = 0.0   # sub-pixel remainder
    last_ka = time.time()
    try:
        while True:
            if time.time() - last_ka > 2:
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
                if mid != bp.MSG_SPATIAL_AUDIO_DATA or not ok:
                    continue
                q = bp.decode_grv(payload)
                if not q:
                    continue
                q = qnorm(q)
                if prev is not None:
                    rv = rotvec(qmul(qconj(prev), q))   # rotation in the sensor's own frame
                    vx = rv[args.x_axis] if abs(rv[args.x_axis]) > args.deadzone else 0.0
                    vy = rv[args.y_axis] if abs(rv[args.y_axis]) > args.deadzone else 0.0
                    fx = fx * args.smooth + vx * (1 - args.smooth)
                    fy = fy * args.smooth + vy * (1 - args.smooth)
                    px = fx * args.sens * sx + rx
                    py = fy * args.sens * sy + ry
                    dx, dy = int(px), int(py)
                    rx, ry = px - dx, py - dy
                    if args.dry_run:
                        if dx or dy:
                            print(f"dx={dx:+d} dy={dy:+d}")
                    else:
                        move(dx, dy)
                prev = q
    except KeyboardInterrupt:
        pass
    finally:
        try:
            s.send(bp.build(bp.MSG_SPATIAL_AUDIO_CONTROL, bytes([bp.CTRL_DETACH])))
            s.send(bp.build(bp.MSG_SET_SPATIAL_AUDIO, bytes([0])))
        except OSError:
            pass
        s.close()


if __name__ == "__main__":
    main()
