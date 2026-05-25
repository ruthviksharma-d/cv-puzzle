# 🧩 Gesture Puzzle v2

An interactive hand gesture–controlled sliding puzzle game built with **OpenCV** and **MediaPipe Hands**. Control the game entirely through natural hand movements—no mouse or keyboard required.

## 🎯 Features

### 🎮 Gesture-Based Interaction
- Real-time hand tracking using MediaPipe
- Smooth gesture-controlled cursor
- Pinch gesture for selecting and moving puzzle tiles
- Open-palm gesture for starting, pausing, and resuming gameplay
- Thumbs-up gesture for restarting the puzzle or returning to the main menu

### 🧩 Multiple Difficulty Levels
Choose from three puzzle sizes:

| Difficulty | Grid Size |
|------------|-----------|
| Easy | 3 × 3 |
| Medium | 4 × 4 |
| Hard | 5 × 5 |

### 🖼 Multiple Image Sources
- Use a live camera frame as the puzzle image
- Select from preloaded local images

### 📊 Advanced Gameplay Features
- Move counter
- Real-time timer
- Performance-based scoring system
- Best-score tracking per difficulty level
- Puzzle completion statistics
- Hint system with limited uses
- Pause and resume functionality

### ✨ Enhanced User Experience
- Animated gesture cursor
- Smooth cursor trail effects
- Tile hover highlighting
- Shuffle animation before gameplay
- Confetti celebration on completion
- Clean heads-up display (HUD)
- Gesture-controlled navigation menus

---

## 🛠 Technologies Used

- Python
- OpenCV
- MediaPipe Hands
- NumPy

---

## 📂 Project Structure

```text
Gesture-Puzzle-v2/
│
├── main.py            # Application entry point
├── hand_tracker.py    # Hand tracking and gesture detection
├── puzzle.py          # Puzzle generation and game logic
├── ui_manager.py      # Rendering and UI components
├── game_manager.py    # State management and scoring
│
├── requirements.txt
├── README.md
└── assets/
```

---

## 🚀 Installation

### Clone the Repository

```bash
git clone https://github.com/your-username/gesture-puzzle-v2.git
cd gesture-puzzle-v2
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Run the Application

```bash
python main.py
```

---

## 🎮 Controls

### Hand Gestures

| Gesture | Function |
|----------|----------|
| ☝️ Index Finger | Move cursor |
| 🤏 Pinch | Select and drag puzzle pieces |
| 🖐️ Open Palm (hold 1 second) | Start game / Pause / Resume |
| 👍 Thumbs Up (hold 1 second) | Restart puzzle / Return to menu |
| ✌️ Two Index Fingers | Define puzzle area in camera mode |

### Keyboard Shortcuts

| Key | Function |
|-----|----------|
| H | Use a hint |
| M | Return to main menu |
| ESC | Exit application |

---

## 🔄 Game Flow

```text
Main Menu
    │
    ├── Select Difficulty
    │
    ├── Select Image Source
    │
    ▼
Puzzle Generation
    │
    ▼
Shuffle Animation
    │
    ▼
Gameplay
    │
    ├── Open Palm → Pause
    ├── Hint System
    └── Thumbs Up → Restart
    │
    ▼
Puzzle Solved
    │
    ▼
Win Screen
    │
    ▼
Main Menu
```

---

## 💡 Adding Custom Images

Place image files inside the project directory and update the image list in `main.py`.

Example:

```python
PRELOADED_IMAGES = [
    "landscape.jpg",
    "mountains.png",
    "my_photo.jpg"
]
```

Supported formats:

- JPG
- JPEG
- PNG

---

## 📈 Scoring System

Final score is calculated using completion time and number of moves:

```text
Score = max(0, 10000 - (Time × 10) - (Moves × 50))
```

Higher scores indicate faster and more efficient puzzle completion.

---

## 🏆 Future Enhancements

- Online leaderboard
- Multiplayer puzzle races
- Mobile support
- Gesture customization
- Sound effects and music
- Cloud score synchronization
- Browser-based version using MediaPipe JavaScript

---

## 📸 Preview

Gesture Puzzle combines computer vision and interactive gameplay to create a touchless puzzle-solving experience powered entirely by hand gestures.

---

## 📄 License

This project is licensed under the MIT License.

See the `LICENSE` file for details.
