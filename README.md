# Smart Inventory Optimization Platform Using IIoT and Real-Time Analytics

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![OpenCV](https://img.shields.io/badge/OpenCV-4.5+-green.svg)
![Tkinter](https://img.shields.io/badge/GUI-Tkinter-lightgrey.svg)
![ESP32](https://img.shields.io/badge/Hardware-ESP32--CAM-orange.svg)
![License](https://img.shields.io/badge/License-MIT-purple.svg)

> ⚠️ **NOTICE: GRADUAL ROLLOUT IN PROGRESS** ⚠️  
> *The source code for this modular project is being uploaded gradually. If some files or modules appear to be missing, please check back soon! The complete architecture is documented below.*

A modular, production-grade desktop application built for real-time industrial inventory management. By integrating an **ESP32-CAM** via local network communication with a **Python/OpenCV** backend, this platform automates stock counting through object detection and provides real-time low-stock alerts on a modern GUI dashboard.

---

## ✨ Features

- **Real-Time IIoT Integration**: Connects seamlessly with an ESP32-CAM over HTTP to fetch live video streams and high-resolution snapshots.
- **Automated Stock Counting**: Utilizes an OpenCV computer vision pipeline (grayscale conversion, Gaussian blur, adaptive thresholding, and contour detection) to identify and count items on the factory/warehouse floor.
- **Modern Dashboard**: A clean, dark-themed Tkinter GUI featuring custom widgets, progress bars, and pulse badges.
- **Smart Inventory Management**: Add, monitor, and manage custom inventory items with specific restock thresholds.
- **Automated Alerts**: Real-time logging system that triggers visual warnings and logs when stock drops below predefined safe levels.
- **Multi-threaded Architecture**: Ensures the GUI remains highly responsive while video streaming and heavy CV processing run in the background.

## 📁 Project Structure

The codebase adheres to SOLID principles and clean code architecture, split into functional modules:

```text
Smart-Inventory-Optimization-IIoT/
│
├── main.py              # Application entry point
├── gui.py               # Main Tkinter application assembly (InventoryApp)
├── detector.py          # OpenCV image processing and object detection pipeline
├── inventory.py         # Inventory business logic and state management
├── camera.py            # ESP32-CAM communication, streaming, and threading
├── alerts.py            # Real-time alert logging and notification system
├── widgets.py           # Custom Tkinter UI components (Cards, Badges, Bars)
├── config.py            # System configuration, theme colors, and camera URLs
│
├── assets/              # Static assets (icons, placeholder images)
├── Arduino/             # ESP32-CAM C++ sketch for the web server
│
├── requirements.txt     # Python dependencies
├── README.md            # Project documentation
└── LICENSE              # MIT License

```

## 🛠️ Hardware Requirements

* **ESP32-CAM Module** (with OV2640 camera)
* FTDI Programmer (for flashing the ESP32)
* 5V Power Supply
* Wi-Fi Network

## 💻 Software Requirements & Installation

1. **Clone the repository:**
```bash
git clone [https://github.com/yourusername/Smart-Inventory-Optimization-IIoT.git](https://github.com/yourusername/Smart-Inventory-Optimization-IIoT.git)
cd Smart-Inventory-Optimization-IIoT

```


2. **Create a Virtual Environment (Recommended):**
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate

```


3. **Install Dependencies:**
```bash
pip install -r requirements.txt

```


*Primary dependencies include `opencv-python`, `numpy`, and `Pillow`.*

## 🚀 Usage Guide

### 1. Configure the ESP32-CAM

1. Open the Arduino IDE and navigate to the `Arduino/` folder.
2. Open the ESP32-CAM sketch.
3. Replace the `ssid` and `password` variables with your Wi-Fi credentials.
4. Flash the code to your ESP32-CAM.
5. Open the Serial Monitor to find the IP address assigned to the camera.

### 2. Configure the Python App

1. Open `config.py` in the project root.
2. Locate the `DEFAULT_IP` variable.
3. Update it with the IP address printed on your Arduino Serial Monitor:
```python
DEFAULT_IP = "192.168.1.XXX"

```



### 3. Run the Platform

Start the application by running the main executable file:

```bash
python main.py

```

### 4. Using the Dashboard

* **Add Items**: Click the "Add Item" button to create a new tracking profile (Name, Total Capacity, Restock Threshold).
* **Assign Camera**: Select the active inventory item from the dropdown menu in the Camera Panel.
* **Process Frame**: Click "Process Frame" to capture a snapshot, run the OpenCV detection pipeline, and update the stock count automatically.

## 🧠 Under the Hood (Computer Vision Pipeline)

The object detection mechanism relies on a robust thresholding technique rather than deep learning, ensuring high speed on edge/desktop hardware:

1. **Grayscale Conversion**: Simplifies the image matrix.
2. **Gaussian Blur**: Reduces high-frequency noise.
3. **Adaptive Thresholding**: Handles uneven lighting environments perfectly.
4. **Morphological Closing**: Fills in gaps inside detected objects.
5. **Contour Area Filtering**: Discards artifacts that are too small or too large based on parameters in `config.py`.

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](https://www.google.com/search?q=LICENSE) file for details.

## 🤝 Contributing

Contributions, issues, and feature requests are welcome! Feel free to check the [issues page](https://www.google.com/search?q=https://github.com/yourusername/Smart-Inventory-Optimization-IIoT/issues).

```

```
