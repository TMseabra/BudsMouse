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
| Buds3 Pro uses the same / compatible messages | ❓ Needs testing |
| Sensors stay active while the earbuds are **in the case** | ❓ Needs testing — earbuds normally detect the case and switch to charging, which may disable sensors and the Bluetooth link |
| Works with the **lid closed** | ❓ Unlikely — the earbuds usually disconnect when the lid closes |
| The case itself exposes motion data | ❌ No evidence the case has a motion sensor or its own data link |
| Head-tracking can be enabled without the Galaxy Wearable app | ❓ Needs testing |

> ⚠️ **Note on Bleak:** Bleak only speaks **BLE**. Since the Buds' control protocol runs over **RFCOMM**, the plan is to use Python's built-in `socket` (`AF_BLUETOOTH` / `BTPROTO_RFCOMM`, supported on Windows) instead. Bleak may still be used for scanning / exploring BLE advertisements.

### Fallback plan

If the sensors turn off inside the case, the project will test the same pipeline **with the earbuds held outside the case** (e.g. both buds in the hand) to at least prove the cursor-control part.

## 🗺️ Roadmap

- [ ] **Phase 1 — Bluetooth:** discover the Buds3 Pro, list services (SPP/RFCOMM + BLE), log raw traffic
- [ ] **Phase 2 — Sensors:** try to enable head tracking and read gyro/accelerometer data; test in case (lid open / closed); live plot
- [ ] **Phase 3 — Mouse control:** map motion to X/Y, sensitivity, smoothing, calibration / neutral position, dead zone
- [ ] **Phase 4 — Clicks:** research gestures (tilt, flick, shake) or other mechanisms for left / right / double click and scroll
- [ ] **Phase 5 — App:** small Windows GUI — on/off, connection status, sensitivity, calibration, axis inversion, gesture toggle

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
