"""Phase 1a - discover the Buds3 Pro.

Lists:
  * Bluetooth Classic devices already paired in Windows (needed for RFCOMM)
  * BLE devices advertising nearby (optional, needs `bleak`)

Usage:
    python phase1_discover.py            # paired devices + 8s BLE scan
    python phase1_discover.py --no-ble
"""
import argparse
import asyncio
import json
import subprocess

PS_PAIRED = (
    "Get-PnpDevice -Class Bluetooth | "
    "Where-Object { $_.InstanceId -like 'BTHENUM\\DEV_*' } | "
    "Select-Object FriendlyName, InstanceId, Status | ConvertTo-Json"
)


def paired_devices():
    out = subprocess.run(
        ["powershell", "-NoProfile", "-Command", PS_PAIRED],
        capture_output=True, text=True,
    ).stdout.strip()
    if not out:
        return []
    data = json.loads(out)
    if isinstance(data, dict):
        data = [data]
    devices = []
    for d in data:
        # InstanceId looks like BTHENUM\DEV_AABBCCDDEEFF\...
        mac = d["InstanceId"].split("DEV_")[1][:12]
        mac = ":".join(mac[i:i + 2] for i in range(0, 12, 2))
        devices.append((d["FriendlyName"], mac, d["Status"]))
    return sorted(set(devices))


async def ble_scan(seconds):
    from bleak import BleakScanner

    found = await BleakScanner.discover(timeout=seconds, return_adv=True)
    for addr, (dev, adv) in found.values():
        yield addr, dev.name or adv.local_name or "?", adv.rssi


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-ble", action="store_true")
    ap.add_argument("--seconds", type=float, default=8)
    args = ap.parse_args()

    print("== Paired Bluetooth devices (Windows) ==")
    for name, mac, status in paired_devices():
        flag = "  <-- Buds?" if "buds" in name.lower() else ""
        print(f"{mac}  {name}  [{status}]{flag}")

    if args.no_ble:
        return
    print(f"\n== BLE scan ({args.seconds:.0f}s) ==")

    async def run():
        async for addr, name, rssi in ble_scan(args.seconds):
            flag = "  <-- Buds?" if "buds" in name.lower() else ""
            print(f"{addr}  {name}  rssi={rssi}{flag}")

    try:
        asyncio.run(run())
    except ImportError:
        print("bleak not installed: pip install -r requirements.txt")


if __name__ == "__main__":
    main()
