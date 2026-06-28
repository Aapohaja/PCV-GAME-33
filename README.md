# Game 33 - Computer Vision Card Game

A real-time Python application combining **OpenCV Computer Vision** and a **Tkinter Graphical User Interface (GUI)** to play a card game called "Game 33" against a computer opponent using real-world physical playing cards scanned via webcam.

---

## 📌 Features

- **Real-time Card Detection**: Uses OpenCV contour extraction (`Canny`, contour analysis) and perspective transform (`warpPerspective`) to isolate and align playing cards from a camera feed.
- **Template Matching**: Matches scanned card features against predefined templates (`cv2.matchTemplate`), supporting both normal and 180-degree rotated cards.
- **Interactive Tkinter UI**: Displays live video feed with bounding contour overlays, visual card previews, round tracking, player/computer hands, and interactive buttons.
- **"Game 33" Game Mechanics**:
  - Max 10 rounds per game.
  - Objective: Reach a hand score closest to **33** without exceeding it (Bust).
  - Computer AI that calculates optimal card retention strategies.
  - Interactive card discarding mechanism.

---

## 🛠️ Requirements & Dependencies

Ensure you have Python 3.8+ installed. Install the required Python packages using `pip`:

```bash
pip install opencv-python numpy pillow
```

---

## 🚀 Setup & Configuration

1. **Card Templates Folder**:
   - `fix.py` matches cards against template images stored on your system.
   - By default, the path is set in `fix.py` on line 12:
     ```python
     PATH_FOLDER = r"C:\Users\aaron\Downloads\individual_cards_2"
     ```
   - Make sure your template folder contains images formatted as `{Rank}_{Suit}.jpg` (e.g., `A_Heart.jpg`, `10_Spade.jpg`). Update `PATH_FOLDER` in `fix.py` to match your local dataset path.

2. **Webcam Selection**:
   - If using an external webcam, update the camera index in `fix.py` (line 92):
     ```python
     self.cap = cv2.VideoCapture(0) # Change 0 to 1 or 2 if needed
     ```

---

## 🎮 How to Play

1. Run the script:
   ```bash
   python fix.py
   ```
2. Click **MULAI GAME** in the GUI.
3. Place a card in front of the camera against a high-contrast (dark) background.
4. When the camera highlights and identifies the card, press **[SPASI] (Spacebar)** to register it into your hand.
5. Draw and discard cards strategically each round to get as close to **33** points as possible without exceeding it!

---

## 📝 Rules & Scoring

| Card Rank | Value |
|-----------|-------|
| 2 - 10    | Face Value (2 - 10) |
| J, Q, K   | 10 points each |
| Ace (A)   | 11 points |

- **Winning Condition**: Highest score $\le 33$ after 10 rounds, or reaching exactly 33 (Instant Win), or if the computer busts.
