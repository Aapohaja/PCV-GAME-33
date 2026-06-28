<div align="center">

# 🎴 Game 33 — Real-Time Computer Vision Card Game

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.x-green.svg?style=for-the-badge&logo=opencv&logoColor=white)](https://opencv.org/)
[![Tkinter](https://img.shields.io/badge/GUI-Tkinter-orange.svg?style=for-the-badge)](https://docs.python.org/3/library/tkinter.html)
[![License](https://img.shields.io/badge/License-MIT-purple.svg?style=for-the-badge)](LICENSE)

**An interactive desktop application integrating real-time Computer Vision (CV), Homography/Perspective Transformation, and Heuristic AI to play physical playing card games.**

[Key Features](#-key-features) • [System Architecture](#-system-architecture) • [Tech Stack](#-tech-stack) • [Installation](#-installation--getting-started) • [Game Rules](#-game-rules--scoring)

</div>

---

## 💡 Overview & Engineering Value

**Game 33** bridges physical interaction with digital artificial intelligence. Instead of manually clicking digital cards, players use **real physical playing cards** scanned in real-time via a webcam.

The application leverages custom computer vision algorithms to detect card geometry, correct perspective distortion, perform template matching under varying orientations, and manage an algorithmic computer opponent programmed with combinatorial optimization strategies.

> 🌟 **Why Recruiters Love This Project**: Demonstrates practical expertise in real-time signal processing, image preprocessing pipelines, spatial transformations, GUI thread management, and game decision algorithms.

---

## ⚙️ System Architecture

The workflow below illustrates the pipeline from physical webcam frame capture to AI decision execution:

```mermaid
graph TD
    A[Webcam Feed] --> B[Grayscale & Gaussian Blur]
    B --> C[Canny Edge Detection]
    C --> D[Contour Analysis & Quadrilateral Approximation]
    D --> E[Perspective Transformation / Bird's-Eye View]
    E --> F[Normalized Template Matching]
    F -->|Match Confidence > 60%| G[GUI State Machine / Buffer]
    G -->|Player Input [SPACE]| H[Player Hand Updated]
    H --> I[Combinatorial Computer AI Move]
    I --> J[Win / Loss / Discard Evaluation]
```

---

## 🔥 Key Features

### 📸 1. Computer Vision & Optical Pipeline
- **Quad Corner Detection**: Extracts high-contrast card contours using `Canny` edge detection and `approxPolyDP` to isolate exact card coordinates.
- **Bird's-Eye View Homography**: Applies perspective warping (`getPerspectiveTransform` & `warpPerspective`) to normalize skewed card angles into a flat 200x280 reference matrix.
- **Rotation-Invariant Template Matching**: Evaluates Normalized Cross-Correlation (`TM_CCOEFF_NORMED`) across 52 pre-computed card templates, accounting for 0° and 180° physical orientation.

### 🧠 2. Heuristic Computer Opponent (AI)
- **Combinatorial Optimization**: Uses `itertools.combinations` to analyze all possible 3-card hand combinations ($O(\binom{N}{3})$) to find the mathematically optimal hand closest to target score 33.
- **Dynamic Risk Assessment**: Evaluates bust risk dynamically to minimize score difference against the player.

### 🖥️ 3. Modern Desktop GUI
- **Real-Time Video Overlay**: Displays live camera feed with visual bounding contours, confidence percentage indicators, and cropped card preview debug windows.
- **Asynchronous Event Loop**: Runs OpenCV frame processing smoothly inside Tkinter’s `after()` scheduling loop without freezing the GUI.

---

## 🛠️ Tech Stack & Dependencies

| Layer | Technology | Purpose |
| :--- | :--- | :--- |
| **Core Language** | Python 3.8+ | Primary software architecture |
| **Computer Vision** | OpenCV (`cv2`) | Image processing, contour analysis, template matching |
| **Numeric Processing** | NumPy | Matrix operations, perspective transformation coordinates |
| **GUI Framework** | Tkinter & Pillow (PIL) | Responsive desktop UI and image-to-canvas rendering |
| **Algorithm Execution** | Standard Library (`itertools`, `random`) | Deck shuffling and combinatorial AI evaluation |

---

## 🚀 Installation & Getting Started

### 1. Clone Repository
```bash
git clone https://github.com/Aapohaja/PCV-GAME-33.git
cd PCV-GAME-33
```

### 2. Install Dependencies
```bash
pip install opencv-python numpy pillow
```

### 3. Run Application
```bash
python fix.py
```

> 📌 **Note on Templates**: The dataset template folder (`individual_cards_2/`) is pre-packaged within this repository and automatically resolved via relative pathing in `fix.py`.

---

## 🎮 Game Rules & Scoring

The objective is to achieve a total hand score as close to **33** as possible over **10 rounds** without going over.

### Card Valuation Table

| Card Rank | Point Value | Notes |
| :---: | :---: | :--- |
| **2 – 10** | Face Value ($2 - 10$) | Standard numerical points |
| **J, Q, K** | 10 Points | Jack, Queen, King face cards |
| **Ace (A)** | 11 Points | Fixed high-value card |

### Gameplay Flow
1. Click **MULAI GAME** to initiate deck shuffling and deal 3 hidden cards to the Computer.
2. Hold a card over a dark background until the webcam feed displays **SIAP: [Rank] [Suit]**.
3. Press **[SPASI] (Spacebar)** to register the card to your hand.
4. If holding 4 cards, select which card to discard via the GUI panel.
5. Win by reaching **exactly 33**, forcing the Computer to **Bust (>33)**, or holding the closest score to 33 after round 10.

---

## 👨‍💻 Author

Developed as a Computer Vision & Intelligent Systems demonstration.

- **GitHub**: [@Aapohaja](https://github.com/Aapohaja)
- **Repository**: [PCV-GAME-33](https://github.com/Aapohaja/PCV-GAME-33.git)
