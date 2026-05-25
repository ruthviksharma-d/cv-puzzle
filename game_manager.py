import time
import random


class GameManager:
    """
    Manages all game state: mode transitions, scoring, best scores.
    Modes: "menu" | "camera" | "puzzle" | "paused" | "won"
    """

    DIFFICULTIES = [
        {"name": "EASY",   "label": "3x3", "grid": 3},
        {"name": "MEDIUM", "label": "4x4", "grid": 4},
        {"name": "HARD",   "label": "5x5", "grid": 5},
    ]

    IMAGE_SOURCES = ["Camera", "Preloaded"]

    def __init__(self):
        self.mode = "menu"

        # Menu selections
        self.selected_diff = 0       # index into DIFFICULTIES
        self.image_source = 0        # index into IMAGE_SOURCES

        # Gameplay state
        self.start_time = None
        self.end_time = None
        self.elapsed = 0.0
        self.solved = False
        self.score = 0
        self.best_scores = [0, 0, 0]  # per difficulty

        # Puzzle region
        self.sel_x1 = self.sel_y1 = self.sel_x2 = self.sel_y2 = None

        # Dragging state
        self.prev_pinch = False
        self.dragging = False

        # Cursor smoothing
        self.smooth_x = 0
        self.smooth_y = 0

        # Trail
        self.trail = []

        # Shuffle
        self.shuffling = False
        self.shuffle_start = 0
        self.last_shuffle = 0

        # Gesture label feedback (shown briefly)
        self.gesture_label = ""
        self.gesture_label_expire = 0

        # Hover tile
        self.hover_tile = None

    # ─────────────────── Properties ───────────────────

    @property
    def grid_size(self):
        return self.DIFFICULTIES[self.selected_diff]["grid"]

    @property
    def diff_name(self):
        d = self.DIFFICULTIES[self.selected_diff]
        return f"{d['name']} ({d['label']})"

    @property
    def diff_names(self):
        return [f"{d['name']} {d['label']}" for d in self.DIFFICULTIES]

    # ─────────────────── Mode transitions ─────────────────────

    def go_menu(self):
        self.mode = "menu"
        self.solved = False
        self.start_time = None
        self.end_time = None
        self.elapsed = 0.0
        self.trail = []
        self.dragging = False
        self.sel_x1 = self.sel_y1 = self.sel_x2 = self.sel_y2 = None

    def go_camera(self):
        self.mode = "camera"
        self.prev_pinch = False

    def go_puzzle(self, x1, y1, x2, y2):
        self.sel_x1, self.sel_y1 = x1, y1
        self.sel_x2, self.sel_y2 = x2, y2
        self.mode = "puzzle"
        self.solved = False
        self.end_time = None
        self.start_time = None
        self.trail = []
        self.dragging = False
        self.prev_pinch = False
        self.smooth_x = (x1 + x2) // 2
        self.smooth_y = (y1 + y2) // 2
        self._begin_shuffle()

    def _begin_shuffle(self):
        self.shuffling = True
        self.shuffle_start = time.time()
        self.last_shuffle = 0

    def go_paused(self):
        if self.mode == "puzzle":
            self.mode = "paused"
            # record elapsed so far
            if self.start_time:
                self.elapsed = time.time() - self.start_time

    def go_resume(self):
        if self.mode == "paused":
            self.mode = "puzzle"
            # re-offset start_time
            if self.start_time:
                self.start_time = time.time() - self.elapsed

    def go_won(self, elapsed):
        self.mode = "won"
        self.elapsed = elapsed
        self.score = self._calc_score(elapsed)
        if self.score > self.best_scores[self.selected_diff]:
            self.best_scores[self.selected_diff] = self.score

    def _calc_score(self, elapsed):
        from puzzle import Puzzle
        base = 10000
        time_penalty = int(elapsed * 10)
        move_penalty = self._move_count * 50
        return max(0, base - time_penalty - move_penalty)

    # ─────────────────── Menu gesture navigation ──────────────────────

    def menu_pinch_action(self, px, py, w, h):
        """
        When user pinches on the menu, check what they're clicking.
        Returns: "start" | "diff_N" | "src_N" | None
        """
        # Difficulty buttons region
        diff_y = h // 2 - 55
        total_w = len(self.DIFFICULTIES) * 160
        start_x = (w - total_w) // 2
        for i in range(len(self.DIFFICULTIES)):
            bx = start_x + i * 160
            by = diff_y
            if bx <= px <= bx + 145 and by <= py <= by + 50:
                self.selected_diff = i
                return f"diff_{i}"

        # Source buttons region
        src_y = h // 2 + 45
        total_sw = len(self.IMAGE_SOURCES) * 200
        start_sx = (w - total_sw) // 2
        for i in range(len(self.IMAGE_SOURCES)):
            bx = start_sx + i * 200
            by = src_y
            if bx <= px <= bx + 185 and by <= py <= by + 50:
                self.image_source = i
                return f"src_{i}"

        return None

    # ─────────────────── Shuffle update ─────────────────────────────

    def update_shuffle(self, puzzle):
        if not self.shuffling:
            return
        now = time.time()
        duration = 1.5 + self.grid_size * 0.3   # longer for harder puzzles
        if now - self.shuffle_start < duration:
            if now - self.last_shuffle > 0.04:
                n = len(puzzle.tiles)
                i = random.randint(0, n - 1)
                j = random.randint(0, n - 1)
                puzzle.swap(i, j)
                self.last_shuffle = now
                puzzle.move_count = 0   # don't count shuffle swaps
        else:
            self.shuffling = False
            self.start_time = time.time()

    # ─────────────────── Gesture label ──────────────────────────────

    def set_gesture_label(self, label, duration=1.5):
        self.gesture_label = label
        self.gesture_label_expire = time.time() + duration

    def get_gesture_label(self):
        if time.time() < self.gesture_label_expire:
            return self.gesture_label
        return ""

    # ─────────────────── Move count cache ────────────────────────────
    # We store move_count in puzzle, but cache here for win screen

    def cache_moves(self, puzzle):
        self._move_count = puzzle.move_count