# ErgoScan

ErgoScan is a posture monitoring and movement detection tool built with **Python**, **MediaPipe**, and **OpenCV**.  
It detects full-body landmarks (pose, hands, and face) in real time using your webcam, helping users become more aware of their posture and movement habits.

---

## Features

- Real-time **full-body landmark detection** (pose, hands, and face)
- Built using **MediaPipe Holistic** model
- Visualizes landmark points and body connections using **OpenCV**
- Runs locally on any system with a webcam

---

## Prerequisites

Make sure you have:

- **Python 3.8+** installed
- A working **webcam**
- A virtual environment tool such as `venv`

---

## Local and Virtual Setup

### 1. Clone the repository

```bash
git clone https://github.com/your-username/ergo-scan.git
cd ergo-scan
```

### 2. Create and activate a Virtual Enviornment

## Windows

```bash
python -m venv venv
venv\Scripts\activate

```

## macOS/Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install mediapipe opencv-contrib-python caer
```

- caer provides helpful utilities for image processing.

## Running the ErgoScan application

Once dependencies are installed and your virtual environment is activated, run:

```bash
python full_body_detection.py
```

If your camera does not open, try changing the camera index inside the file to 0 or 1:

```bash
cap = cv2.VideoCapture(0)
```

or

```bash
cap = cv2.VideoCapture(1)
```

Press q on the appeared screen to quit the application.
