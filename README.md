<div align="center">

# Cari 33

**Play card games with real physical cards, not clicks.**

A desktop card game where a webcam reads your actual playing cards in real time. Built to explore computer vision on a problem that's easy to demo and fun to show off.

[Watch the demo →](https://youtu.be/A00Md_RPhA0)

![Python](https://img.shields.io/badge/Python-3.8+-3776AB?logo=python&logoColor=white)
![OpenCV](https://img.shields.io/badge/OpenCV-4.x-5C3EE8?logo=opencv&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-A855F7)

</div>

---

## What it does

You hold a real playing card in front of your webcam. The app detects its edges, warps the tilted view into a flat image, and matches it against 52 templates. Once it's confident, you press Space to add the card to your hand.

Your goal is to build a hand as close to **33** as possible over 10 rounds without going over. A computer opponent plays against you, scanning all its 3-card combinations to pick the best move.

That's it. No mouse. No touchscreen. Just cardboard and a camera.

---

## Quick start

```bash
git clone https://github.com/Aapohaja/PCV-GAME-33.git
cd PCV-GAME-33
pip install opencv-python numpy pillow
python fix.py
```

The card templates in `individual_cards_2/` ship with the repo, so you're ready to play right after install.

---

## How to play

1. Click **MULAI GAME**. The computer draws 3 hidden cards.
2. Hold a card in front of the webcam. Wait until the feed shows `SIAP: [Rank] [Suit]`.
3. Press **Space** to register the card into your hand.
4. Already have 4 cards? Pick one to discard from the GUI panel.
5. Win by:
   - hitting exactly **33**, or
### Card values

| Card | Points |
|:----:|:------:|
| 2–10 | face value |
| J, Q, K | 10 |
| A | 11 |

---

## How it works

The vision pipeline runs on every webcam frame:

```
Webcam frame
  ↓  grayscale + Gaussian blur
  ↓  Canny edge detection
  ↓  contour analysis (approxPolyDP)
  ↓  perspective warp to flat 200×280
  ↓  template matching against 52 cards
  ↓  confidence > 60% → ready to register
```

The AI opponent is simpler than the vision side. It brute-forces every 3-card combination in its hand with `itertools.combinations`, scores each one, and picks whichever gets closest to 33 without busting.

Both loops run inside Tkinter's `after()` scheduler so the video feed stays smooth without freezing the UI.

---

## Tech stack

- **Python 3.8+** — everything runs here
- **OpenCV** — edge detection, contour analysis, perspective warp, template matching
- **NumPy** — matrix math for the warp
- **Tkinter + Pillow** — GUI and rendering the live camera feed

---

## Why this project

I wanted to build something that made computer vision feel tangible instead of academic. Card recognition is a well-understood problem with a huge visual payoff — the moment you hold up

## Author

**Aaron Smeraldo Olivier Manik**
Computer Engineering, ITS Surabaya

[GitHub](https://github.com/Aapohaja) · [LinkedIn](https://linkedin.com/in/aaron-manik)


