# 🧩 Gesture Puzzle v2

A real-time gesture-controlled puzzle game built with **OpenCV** and **MediaPipe**.  
No mouse. No keyboard. Just your hands.

---

## ✨ What's New in v2

| Feature | v1 | v2 |
|---|---|---|
| Difficulty levels | Fixed 3×3 | Easy / Medium / Hard (3×3 → 5×5) |
| Main menu | ❌ | ✅ Gesture-navigable menu |
| Image source | Camera only | Camera + Preloaded images |
| Move counter | ❌ | ✅ Real-time |
| Scoring | ❌ | ✅ Score = f(time, moves); best score saved |
| Hint system | ❌ | ✅ 3 hints per game (press `h`) |
| Pause | ❌ | ✅ Open palm gesture |
| Restart | ❌ | ✅ Thumbs-up gesture |
| Tile hover | ❌ | ✅ Subtle highlight under cursor |
| Win screen | Basic text | ✅ Confetti + stats + score |
| Cursor | Static dot | ✅ Adaptive, animated cursor |
| Trail | Static | ✅ Fading color trail |
| HUD | Scattered | ✅ Clean top/bottom bars |
| Architecture | 1 file | ✅ 4 modules |

---

## 🛠 Installation

```bash
git clone https://github.com/molly22-byte/hand-gesture-puzzle.git
cd hand-gesture-puzzle
pip install -r requirements.txt
python main.py
```

---

## 🎮 Gesture Controls

| Gesture | Action |
|---|---|
| ☝️ **Index finger** | Move cursor |
| 🤏 **Pinch** | Select / drag tile; choose menu option |
| 🖐️ **Open palm** (hold 1s) | Start game from menu / Pause in game |
| 👍 **Thumbs up** (hold 1s) | Restart puzzle / Back to menu from win screen |
| ✌️ **Both index fingers** | Frame puzzle area (camera mode) |

### Keyboard shortcuts
| Key | Action |
|---|---|
| `H` | Activate hint (keyboard fallback) |
| `M` | Return to main menu |
| `ESC` | Quit |

---

## 🧠 UX Flow

```
Main Menu
  ↓ (select difficulty + source → open palm)
Camera Mode      OR      Preloaded Image
  ↓ (frame area + pinch)        ↓ (auto)
Shuffle Animation
  ↓
Gameplay  ──── (open palm) ──→ Paused ──── (open palm) ──→ resume
  ↓                               ↓ (thumbs up)
Win Screen ←─────────────── restart
  ↓ (thumbs up)
Main Menu
```

---

## 📁 Project Structure

```
main.py           # Main loop + orchestration
hand_tracker.py   # MediaPipe hand tracking + gesture detection
puzzle.py         # Tile logic, hints, hover, scoring
ui_manager.py     # All rendering: menu, HUD, win screen, confetti
game_manager.py   # State machine, difficulty, scores
requirements.txt
README.md
```

---

## 🖼 Adding Preloaded Images

Drop `.jpg` or `.png` files into the project folder and update `PRELOADED_IMAGES` at the top of `main.py`:

```python
PRELOADED_IMAGES = [
    "my_photo.jpg",
    "landscape.png",
]
```

---

## 📊 Scoring

```
Score = max(0, 10000 - elapsed_seconds × 10 - moves × 50)
```

Best score is saved per difficulty level for the session.

---

## 🚀 v3 Ideas

- 🎮 Multiplayer race mode
- 🌐 Web version (MediaPipe JS)
- 📱 Mobile (touch + gesture)
- 🔊 Sound feedback
- 🏆 Persistent leaderboard
