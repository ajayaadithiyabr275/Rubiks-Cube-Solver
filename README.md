# 🧊 Rubik’s Cube Solver using Computer Vision & Python

A real-time **Rubik’s Cube Solver** built with **Python, OpenCV, and the Kociemba algorithm**.  
It scans all 6 faces of a physical cube through a **webcam**, detects sticker colors using **HSV color thresholds**, and then computes and guides you through the optimal solving moves.

---

## 🚀 Features
- Real-time webcam scanning of all cube faces  
- Accurate HSV-based color classification (improved white detection)  
- Solves cube using **Kociemba’s two-phase algorithm**  
- Visual arrow overlays for move guidance  
- Auto-detects already-solved cubes  
- Shows “✅ CUBE SOLVED!” animation after completion  

---

## 🧰 Requirements
- Python 3.10+
- `opencv-python`
- `numpy`
- `kociemba`

Install with:
```bash
pip install opencv-python numpy kociemba

Rubiks-Cube-Solver/
│
├── Main.py        # Scans, solves, and displays move guidance  
├── State.py       # Viewer (optional for cube visualization)  
├── Resources/     # Arrow images (U.png, R.png, F'.png, etc.)  
└── hsv_calibration.json  # Optional HSV color calibration file  

## 🚀 Getting Started

1. **Install dependencies**  
   ```bash
   pip install opencv-python numpy kociemba
   ```

2. **Run the viewer** (in one terminal)  
   ```bash
   python State.py
   ```

3. **Run the solver** (in another terminal)  
   ```bash
   python Main.py
   ```

## 🎮 Controls

- **During scanning (Main.py)**  
  - Press `U`, `R`, `F`, `D`, `L`, `B` to scan that face  
  - Press `ESC` once all six faces are scanned  

- **During solving**  
  - Press `SPACE` to confirm each move  
  - Press `ESC` to exit at any time  


