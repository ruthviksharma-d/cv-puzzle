import numpy as np
import random
import cv2
import time


class Puzzle:
    def __init__(self, grid_size=3):
        self.grid_size = grid_size
        self.tiles = []
        self.original_tiles = []
        self.tile_positions = []   # for smooth sliding animation
        self.tile_targets = []
        self.selected = None
        self.move_count = 0

        # Hint system
        self.hint_tile = None
        self.hint_start = None
        self.hints_remaining = 3
        self.hint_duration = 2.0  # seconds to show hint

    def create(self, frame):
        h, w, _ = frame.shape
        th, tw = h // self.grid_size, w // self.grid_size

        self.tiles = []
        self.original_tiles = []
        self.move_count = 0
        self.selected = None
        self.hint_tile = None
        self.hint_start = None
        self.hints_remaining = 3

        for i in range(self.grid_size):
            for j in range(self.grid_size):
                tile = frame[i * th:(i + 1) * th, j * tw:(j + 1) * tw]
                self.tiles.append(tile.copy())
                self.original_tiles.append(tile.copy())

        random.shuffle(self.tiles)

    def combine(self):
        rows = []
        for i in range(self.grid_size):
            row = np.hstack(self.tiles[i * self.grid_size:(i + 1) * self.grid_size])
            rows.append(row)
        return np.vstack(rows)

    def get_index(self, x, y):
        """Convert normalized local coords (0-1) to tile index."""
        col = min(int(x * self.grid_size), self.grid_size - 1)
        row = min(int(y * self.grid_size), self.grid_size - 1)
        return row * self.grid_size + col

    def swap(self, i, j):
        if i is not None and j is not None and i != j:
            self.tiles[i], self.tiles[j] = self.tiles[j], self.tiles[i]
            self.move_count += 1

    def draw_selected(self, frame, sel_x1, sel_y1, sel_x2, sel_y2):
        if self.selected is None:
            return

        gs = self.grid_size
        pw = sel_x2 - sel_x1
        ph = sel_y2 - sel_y1
        tw = pw // gs
        th = ph // gs

        row = self.selected // gs
        col = self.selected % gs

        x1 = sel_x1 + col * tw
        y1 = sel_y1 + row * th
        x2 = x1 + tw
        y2 = y1 + th

        # Animated pulsing border
        t = time.time()
        alpha = 0.5 + 0.5 * abs(math.sin(t * 4))
        color = (int(0 * alpha + 255 * (1 - alpha)), int(255 * alpha), int(100 * alpha))

        overlay = frame.copy()
        cv2.rectangle(overlay, (x1, y1), (x2, y2), (50, 200, 50), -1)
        cv2.addWeighted(overlay, 0.15, frame, 0.85, 0, frame)
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 100), 3)

    def draw_hint(self, frame, sel_x1, sel_y1, sel_x2, sel_y2):
        """Highlight a misplaced tile that should be moved."""
        if self.hint_tile is None or self.hint_start is None:
            return

        elapsed = time.time() - self.hint_start
        if elapsed > self.hint_duration:
            self.hint_tile = None
            return

        gs = self.grid_size
        pw = sel_x2 - sel_x1
        ph = sel_y2 - sel_y1
        tw = pw // gs
        th = ph // gs

        row = self.hint_tile // gs
        col = self.hint_tile % gs

        x1 = sel_x1 + col * tw
        y1 = sel_y1 + row * th
        x2 = x1 + tw
        y2 = y1 + th

        # Fade out
        fade = 1.0 - (elapsed / self.hint_duration)
        pulse = abs(math.sin(elapsed * 6))
        intensity = int(255 * fade * pulse)

        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, intensity, 255), 4)
        cv2.putText(frame, "HINT", (x1 + 5, y1 + 25),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, intensity, 255), 2)

    def activate_hint(self):
        """Find a misplaced tile and highlight it."""
        if self.hints_remaining <= 0:
            return False

        misplaced = []
        for i in range(len(self.tiles)):
            if not (self.tiles[i] == self.original_tiles[i]).all():
                misplaced.append(i)

        if misplaced:
            self.hint_tile = random.choice(misplaced)
            self.hint_start = time.time()
            self.hints_remaining -= 1
            return True
        return False

    def draw_hover(self, frame, sel_x1, sel_y1, sel_x2, sel_y2, tile_idx):
        """Subtle hover highlight on tile under cursor."""
        if tile_idx is None or self.selected is not None:
            return

        gs = self.grid_size
        pw = sel_x2 - sel_x1
        ph = sel_y2 - sel_y1
        tw = pw // gs
        th = ph // gs

        row = tile_idx // gs
        col = tile_idx % gs

        x1 = sel_x1 + col * tw
        y1 = sel_y1 + row * th
        x2 = x1 + tw
        y2 = y1 + th

        overlay = frame.copy()
        cv2.rectangle(overlay, (x1, y1), (x2, y2), (255, 255, 255), -1)
        cv2.addWeighted(overlay, 0.08, frame, 0.92, 0, frame)
        cv2.rectangle(frame, (x1, y1), (x2, y2), (200, 200, 200), 1)

    def is_solved(self):
        for i in range(len(self.tiles)):
            if not (self.tiles[i] == self.original_tiles[i]).all():
                return False
        return True

    def compute_score(self, elapsed_time):
        """Higher score for fewer moves and faster time."""
        base = 10000
        time_penalty = int(elapsed_time * 10)
        move_penalty = self.move_count * 50
        return max(0, base - time_penalty - move_penalty)


import math