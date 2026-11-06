# BudsMouse 🖱️🎧

> Turn the **Samsung Galaxy Buds3 Pro charging case** into a wireless air mouse for **Windows 11** — software only, no extra hardware.

![status](https://img.shields.io/badge/status-research-orange) ![python](https://img.shields.io/badge/python-3.10%2B-blue) ![platform](https://img.shields.io/badge/platform-Windows%2011-0078D6)

## 💡 The idea

The Galaxy Buds3 Pro earbuds have built-in motion sensors (used for head tracking / 360 Audio).
BudsMouse explores whether those sensors can be read **while the earbuds sit inside their original case**, so that moving the case in your hand moves the mouse cursor on the PC.

1. Put both earbuds in the case (lid open at first).
2. Move the case with your hand.
3. The earbuds' sensors detect the motion.
4. The data is streamed over Bluetooth to the PC.
5. BudsMouse converts it into cursor movement.

### Hard requirements

- Samsung Galaxy Buds3 Pro + original, **unmodified** case
- **No** ESP32, external sensors or any extra hardware
- Bluetooth communication with the PC
- Python 3, Windows 11

## 🔬 Research status

This project is honest about what is known and what is not. Nothing below is assumed to work until it is tested.

| Question | Status |
|---|---|
| Galaxy Buds use a proprietary binary protocol over **Bluetooth Classic SPP/RFCOMM** (not BLE GATT) | ✅ Confirmed by community reverse engineering (GalaxyBudsClient) |
| Older models (Buds Pro) stream gyroscope / head-tracking data over that protocol (`SPATIAL_AUDIO_DATA` messages) | ✅ Confirmed for Buds Pro (BudsPro-Headtracking project) |
| Buds3 Pro uses the same / compatible messages | ✅ Confirmed — same `FD … DD` framing; head-tracking (`SET_SPATIAL_AUDIO` + `SPATIAL_AUDIO_CONTROL Attach`) streams quaternions on **RFCOMM channel 27** from Python |
| Sensors stay active while the earbuds are **in the case** | ❓ Needs testing — earbuds normally detect the case and switch to charging, which may disable sensors and the Bluetooth link |
| Works with the **lid closed** | ❓ Unlikely — the earbuds usually disconnect when the lid closes |
| The case itself exposes motion data | ❌ No evidence the case has a motion sensor or its own data link |
| Head-tracking can be enabled without the Galaxy Wearable app | ✅ Confirmed — enabled directly from `phase2_sensors.py` |

> ⚠️ **Note on Bleak:** Bleak only speaks **BLE**. Since the Buds' control protocol runs over **RFCOMM**, the plan is to use Python's built-in `socket` (`AF_BLUETOOTH` / `BTPROTO_RFCOMM`, supported on Windows) instead. Bleak may still be used for scanning / exploring BLE advertisements.

### Fallback plan

If the sensors turn off inside the case, the project will test the same pipeline **with the earbuds held outside the case** (e.g. both buds in the hand) to at least prove the cursor-control part.

## 🗺️ Roadmap

- [x] **Phase 1 — Bluetooth:** discover the Buds3 Pro, list services (SPP/RFCOMM + BLE), log raw traffic
  - [x] `phase1_discover.py` — lists paired devices + BLE scan (Buds3 Pro found as paired device)
  - [x] `phase1_rfcomm.py` — probes RFCOMM channels 1–30 and hex-dumps raw traffic. Result: channels 20 and 27 speak the Samsung protocol; **27 accepts head-tracking commands**
- [~] **Phase 2 — Sensors:** try to enable head tracking and read gyro/accelerometer data; test in case (lid open / closed); live plot
  - [x] `buds_proto.py` (framing, CRC16, quaternion decoder) + `phase2_sensors.py` — live quaternion stream confirmed
  - [ ] Test with buds **inside the case** (lid open / closed) while moving it — needs a physical test
  - [ ] Live plot
- [~] **Phase 3 — Mouse control:** map motion to X/Y, sensitivity, smoothing, calibration / neutral position, dead zone
  - [x] `phase3_mouse.py` — relative-rotation → cursor movement with sensitivity, smoothing, dead zone, axis mapping/inversion, `--dry-run` (dx/dy output verified; real cursor movement not yet tuned)
  - [ ] Tune axes/sensitivity with the buds in the case (needs a physical test)
- [ ] **Phase 4 — Clicks:** research gestures (tilt, flick, shake) or other mechanisms for left / right / double click and scroll
- [ ] **Phase 5 — App:** small Windows GUI — on/off, connection status, sensitivity, calibration, axis inversion, gesture toggle

## ▶️ Usage (Phase 1)

```bash
pip install -r requirements.txt
python phase1_discover.py                      # find the Buds MAC address
python phase1_rfcomm.py AA:BB:CC:DD:EE:FF      # probe RFCOMM + log raw frames
python phase2_sensors.py AA:BB:CC:DD:EE:FF --channel 27   # stream head-tracking quaternions
python phase3_mouse.py AA:BB:CC:DD:EE:FF --dry-run        # preview cursor deltas (drop --dry-run to move the cursor)
```

Pair the Buds in Windows first, and disconnect them from the phone / Galaxy Wearable while testing.

## 🧰 Planned stack

- Python 3.10+
- `socket` (RFCOMM) for the Buds protocol, `bleak` for BLE exploration
- `pyautogui` or `pynput` for cursor control
- `matplotlib` for live sensor plots
- `tkinter` / `customtkinter` for the GUI

## 📚 References

- [GalaxyBudsClient](https://github.com/timschneeb/GalaxyBudsClient) — unofficial Galaxy Buds manager, protocol reverse engineering
- [BudsPro-Headtracking](https://github.com/timschneeb/BudsPro-Headtracking) — streaming head-tracking data from Buds Pro
- [BudsProAnalysis](https://github.com/ThePBone/BudsProAnalysis) — analysis of the spatial audio message IDs
- [ghetto-spatial-audio](https://github.com/JediRhymeTrix/ghetto-spatial-audio) — Python example using Buds Pro head-tracking on Windows

## ⚖️ Disclaimer

Personal, educational project. Not affiliated with or endorsed by Samsung. Use at your own risk.
