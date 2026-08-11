Cari 33 — Computer Vision Card Game

A desktop card game where you play using real physical playing cards instead of clicks. A webcam reads the cards in real time, and you play against a computer opponent that tries to build a hand closest to 33.

Built with Python, OpenCV, and Tkinter.

Demo video: https://youtu.be/A00Md_RPhA0

https://img.shields.io/badge/Python-3.8%2B-blue
https://img.shields.io/badge/OpenCV-4.x-green
https://img.shields.io/badge/License-MIT-purple

---
How to run

git clone https://github.com/Aapohaja/PCV-GAME-33.git
cd PCV-GAME-33
pip install opencv-python numpy pillow
python fix.py
The card templates in individual_cards_2/ come with the repo, so no extra setup is needed.

---
How to play

Goal: get your hand as close to 33 as possible over 10 rounds without going over.

1. Click MULAI GAME. The computer gets 3 hidden cards.
2. Hold a physical card in front of the webcam over a dark background. Wait until the feed shows SIAP: [Rank] [Suit].
3. Press Space to add the card to your hand.
4. If you already have 4 cards, pick one to discard from the GUI panel.
5. You win if you hit exactly 33, if the computer busts, or if you are closest to 33 after round 10.

Card values

- 2 through 10 — face value (2 to 10 points)
- Jack, Queen, King — 10 points each
- Ace — 11 points

---
How it works

The pipeline from webcam frame to
5. Apply a perspective warp to normalize the tilted card into a flat 200 by 280 image.
6. Match the flat image against 52 pre-computed card templates using normalized cross-correlation. Both 0 degree and 180 degree orientations are checked.
7. If match confidence is above 60 percent, the card is ready to be registered with the Space key.

The computer opponent picks its next move by scanning all 3-card combinations from its hand with itertools.combinations, then picking whichever gets closest to 33 without busting.

The whole thing runs inside Tkinter's after() loop so the video feed stays smooth without freezing the UI.

---
Tech stack

- Python 3.8+ — main language
- OpenCV — image processing, contour detection, template matching
- NumPy — matrix math for perspective transforms
- Tkinter + Pillow — GUI and rendering the webcam feed to the canvas

---
Author

Aaron Smeraldo Olivier Manik — Computer Engineering student at ITS Surabaya.

- OpenCV — image processing, contour detection, template matching
- NumPy — matrix math for perspective transforms
- Tkinter + Pillow — GUI and rendering the webcam feed to the canvas

---
Author

Aaron Smeraldo Olivier Manik — Computer Engineering student at ITS Surabaya.

GitHub: @Aapohaja (https://github.com/Aapohaja)
