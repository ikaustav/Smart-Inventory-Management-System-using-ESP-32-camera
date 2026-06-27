# Smart Inventory Optimization Platform Using IIoT and Real-Time Analytics

A desktop inventory management system that pairs an **ESP32-CAM** with a
**Python + OpenCV + Tkinter** dashboard to automatically count shelf stock in
real time, visualize inventory health, and raise low-stock alerts — all over
a local Wi-Fi network.

> This repository is a **modular refactor** of the original single-file
> prototype. Functionality is 100% identical to the original — the code has
> only been reorganized into clean, single-responsibility modules.

---

## ✨ Features

- Live MJPEG / snapshot video feed from an ESP32-CAM
- Real-time object detection & counting via an OpenCV contour pipeline
- Draggable "shelf zone" region-of-interest selection on the live feed
- Automatic inventory count updates driven by camera detections
- Per-item low-stock / out-of-stock alerts (visual badge + log)
- Animated stock-level bars and a live dashboard summary
- Add/manage inventory items through a simple dialog
- Demo mode for testing the UI without physical hardware
- Works fully offline on a local Wi-Fi network

---

## 🏗️ Architecture

```
ESP32-CAM  →  Wi-Fi  →  Python/OpenCV Detection  →  Inventory Update  →  Dashboard + Alerts
```

1. **Edge (ESP32-CAM):** captures shelf images and serves them over HTTP
   (`/stream` for MJPEG, `/capture` for single snapshots).
2. **Image Processing (OpenCV):** grayscale → Gaussian blur → adaptive
   threshold → morphological closing → contour detection → area filtering →
   object count.
3. **Data Management:** in-memory inventory state, thresholds, and alert log.
4. **Dashboard (Tkinter):** live camera view, inventory cards, stock bars,
   summary bar, and alert log.
5. **Alerts:** visual badges and color-coded log entries when stock is low
   or out.

---

## 📂 Project Structure

```
Smart-Inventory-Optimization-IIoT/
│
├── main.py            # Application entry point
│
├── gui.py             # InventoryApp — assembles the full application
├── camera.py          # CameraPanel — ESP32 streaming/snapshot/threading
├── detector.py        # ObjectDetector — OpenCV contour detection pipeline
├── inventory.py       # InventoryItem — inventory business logic
├── widgets.py         # StockBar, PulseBadge, ItemCard, SummaryBar, AddItemDialog
├── alerts.py          # AlertLog — color-coded alert log widget
├── config.py          # Theme colors, fonts, and constants
│
├── assets/
│   ├── icons/
│   └── images/
│
├── Arduino/           # ESP32-CAM firmware (place your .ino sketch here)
│
├── requirements.txt
├── README.md
├── LICENSE
└── .gitignore
```

### Module responsibilities

| Module | Responsibility |
|---|---|
| `config.py` | Colors, fonts, and constants only — no logic |
| `inventory.py` | `InventoryItem` stock business logic |
| `detector.py` | `ObjectDetector` — OpenCV detection pipeline |
| `camera.py` | `CameraPanel` — ESP32 connection, streaming, snapshots |
| `widgets.py` | Custom Tkinter widgets used by the dashboard |
| `alerts.py` | `AlertLog` alert log widget |
| `gui.py` | `InventoryApp` — wires every module together |
| `main.py` | Launches the application |

---

## 🚀 Getting Started

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the application

```bash
python main.py
```

### 3. Connect your ESP32-CAM

1. Flash your ESP32-CAM with a sketch that serves an MJPEG stream
   (`/stream`) and/or a snapshot endpoint (`/capture`). See `Arduino/`.
2. Enter the ESP32's IP address in the **ESP32 IP** field and click
   **Apply IP**.
3. Click **▶ CONNECT STREAM** (or **📷 SNAPSHOT** for single-frame mode).
4. No hardware yet? Click **DEMO MODE** to preview the dashboard with a
   simulated feed.

### 4. Set a detection zone (optional)

Drag directly on the live camera feed to define a "shelf zone" — only
objects inside that region will be counted. Right-click to clear it.

### 5. Bind the camera to an inventory item

Use the **"Camera updates item"** dropdown to choose which inventory item's
count is automatically driven by the live object count.

---

## 🛠️ Technology Stack

- **Edge:** ESP32-CAM, Arduino IDE, Wi-Fi (HTTP/MJPEG)
- **Backend:** Python 3.x, OpenCV, NumPy, Pillow, Tkinter, urllib, threading

---

## 📋 Requirements

- Python 3.9+
- A Tk-enabled Python installation (Tkinter ships with most standard Python
  installers; on Linux you may need `sudo apt install python3-tk`)
- An ESP32-CAM on the same local network (optional — Demo Mode works without
  one)

---

## 📜 License

This project is licensed under the MIT License — see [LICENSE](LICENSE) for
details.
