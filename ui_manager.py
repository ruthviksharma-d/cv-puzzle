import cv2
import numpy as np
import time
import math


class UIManager:
    """Handles all screen rendering: menu, HUD, overlays, celebrations."""

    # Color palette (BGR)
    C_BG          = (15, 12, 20)
    C_ACCENT      = (80, 220, 130)       # green
    C_ACCENT2     = (220, 160, 40)       # amber
    C_TEXT        = (230, 230, 230)
    C_DIM         = (120, 120, 120)
    C_RED         = (60, 80, 220)
    C_BLUE        = (220, 140, 60)
    C_WHITE       = (255, 255, 255)
    C_GOLD        = (30, 215, 255)

    FONT          = cv2.FONT_HERSHEY_SIMPLEX
    FONT_BOLD     = cv2.FONT_HERSHEY_DUPLEX
    FONT_SCRIPT   = cv2.FONT_HERSHEY_COMPLEX

    def __init__(self, w, h):
        self.w = w
        self.h = h
        self._particles = []   # for confetti
        self._init_time = time.time()

    # ─────────────────────────── UTILITIES ───────────────────────────

    def _t(self):
        return time.time() - self._init_time

    def _overlay_rect(self, frame, x1, y1, x2, y2, color, alpha=0.55, radius=12):
        """Draw a semi-transparent rounded rectangle."""
        overlay = frame.copy()
        # Simulate rounded corners with filled rect (good enough for OpenCV)
        cv2.rectangle(overlay, (x1 + radius, y1), (x2 - radius, y2), color, -1)
        cv2.rectangle(overlay, (x1, y1 + radius), (x2, y2 - radius), color, -1)
        for cx, cy in [(x1 + radius, y1 + radius), (x2 - radius, y1 + radius),
                       (x1 + radius, y2 - radius), (x2 - radius, y2 - radius)]:
            cv2.circle(overlay, (cx, cy), radius, color, -1)
        cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)

    def _text_center(self, frame, text, cy, font_scale, color, thickness=1, font=None):
        if font is None:
            font = self.FONT_BOLD
        (tw, th), _ = cv2.getTextSize(text, font, font_scale, thickness)
        x = (self.w - tw) // 2
        cv2.putText(frame, text, (x, cy), font, font_scale, color, thickness, cv2.LINE_AA)

    def _progress_bar(self, frame, x, y, w, h, progress, color, bg=(50, 50, 50)):
        cv2.rectangle(frame, (x, y), (x + w, y + h), bg, -1)
        fill = int(w * progress)
        if fill > 0:
            cv2.rectangle(frame, (x, y), (x + fill, y + h), color, -1)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (100, 100, 100), 1)

    # ─────────────────────────── MAIN MENU ───────────────────────────

    def draw_main_menu(self, frame, selected_diff, diff_names, image_source,
                       image_sources, open_palm_progress=0.0):
        """Draw the main menu over the camera feed."""
        # Darken camera feed
        dark = np.zeros_like(frame)
        cv2.addWeighted(frame, 0.25, dark, 0.75, 0, frame)

        t = self._t()
        w, h = self.w, self.h

        # Title
        title = "GESTURE PUZZLE"
        pulse = 0.85 + 0.15 * math.sin(t * 2)
        color = (int(80 * pulse), int(220 * pulse), int(130 * pulse))
        self._text_center(frame, title, h // 2 - 180, 1.8, color, 3, self.FONT_SCRIPT)

        subtitle = "Control with your hands"
        self._text_center(frame, subtitle, h // 2 - 130, 0.65, self.C_DIM, 1)

        # ── Difficulty selector ──
        diff_y = h // 2 - 70
        self._text_center(frame, "DIFFICULTY", diff_y, 0.55, self.C_DIM, 1)

        total_w = len(diff_names) * 160
        start_x = (w - total_w) // 2

        for i, name in enumerate(diff_names):
            bx = start_x + i * 160
            by = diff_y + 15
            selected = (i == selected_diff)

            bg_color = (30, 80, 40) if selected else (30, 30, 35)
            border_color = self.C_ACCENT if selected else (80, 80, 80)

            self._overlay_rect(frame, bx, by, bx + 145, by + 50, bg_color, 0.8)
            cv2.rectangle(frame, (bx, by), (bx + 145, by + 50), border_color, 2)

            text_color = self.C_ACCENT if selected else self.C_DIM
            (tw, th), _ = cv2.getTextSize(name, self.FONT_BOLD, 0.65, 2)
            tx = bx + (145 - tw) // 2
            ty = by + (50 + th) // 2
            cv2.putText(frame, name, (tx, ty), self.FONT_BOLD, 0.65, text_color, 2, cv2.LINE_AA)

        # ── Image Source ──
        src_y = h // 2 + 30
        self._text_center(frame, "IMAGE SOURCE", src_y, 0.55, self.C_DIM, 1)

        total_sw = len(image_sources) * 200
        start_sx = (w - total_sw) // 2

        for i, src in enumerate(image_sources):
            bx = start_sx + i * 200
            by = src_y + 15
            selected = (i == image_source)

            bg_color = (40, 40, 90) if selected else (30, 30, 35)
            border_color = self.C_BLUE if selected else (80, 80, 80)

            self._overlay_rect(frame, bx, by, bx + 185, by + 50, bg_color, 0.8)
            cv2.rectangle(frame, (bx, by), (bx + 185, by + 50), border_color, 2)

            text_color = self.C_BLUE if selected else self.C_DIM
            (tw, th), _ = cv2.getTextSize(src, self.FONT_BOLD, 0.55, 1)
            tx = bx + (185 - tw) // 2
            ty = by + (50 + th) // 2
            cv2.putText(frame, src, (tx, ty), self.FONT_BOLD, 0.55, text_color, 1, cv2.LINE_AA)

        # ── Instructions ──
        inst_y = h // 2 + 155
        instructions = [
            ("PINCH", "select option"),
            ("OPEN PALM", "start game  (hold 1s)"),
        ]
        for i, (gesture, action) in enumerate(instructions):
            ix = w // 2 - 250 + i * 310
            iy = inst_y
            self._overlay_rect(frame, ix, iy, ix + 280, iy + 55, (25, 25, 30), 0.7)
            cv2.putText(frame, gesture, (ix + 12, iy + 22),
                        self.FONT_BOLD, 0.55, self.C_ACCENT2, 1, cv2.LINE_AA)
            cv2.putText(frame, action, (ix + 12, iy + 44),
                        self.FONT, 0.45, self.C_DIM, 1, cv2.LINE_AA)

        # ── Open palm progress ──
        if open_palm_progress > 0.01:
            bar_w = 300
            bar_x = (w - bar_w) // 2
            bar_y = h // 2 + 230
            self._text_center(frame, "Hold palm to START...", bar_y - 20, 0.5, self.C_ACCENT, 1)
            self._progress_bar(frame, bar_x, bar_y, bar_w, 12,
                               open_palm_progress, self.C_ACCENT)

        # ── Cursor dot (index finger) ──
        return frame

    def draw_menu_cursor(self, frame, cx, cy, pinching):
        """Draw the interactive cursor on menu."""
        color = self.C_ACCENT if pinching else self.C_WHITE
        size = 8 if pinching else 5
        cv2.circle(frame, (cx, cy), size + 4, (*color, 80), 1)
        cv2.circle(frame, (cx, cy), size, color, -1)

    # ─────────────────────────── CAMERA MODE ──────────────────────────

    def draw_camera_ui(self, frame, two_hands, sel_box, pinching):
        """Overlay for the camera/frame-selection mode."""
        w, h = self.w, self.h

        # Top instruction bar
        self._overlay_rect(frame, 0, 0, w, 60, (15, 12, 20), 0.7, 0)
        cv2.putText(frame, "Use BOTH INDEX FINGERS to frame your puzzle area",
                    (20, 38), self.FONT, 0.65, self.C_ACCENT, 1, cv2.LINE_AA)
        cv2.putText(frame, "Then PINCH to capture",
                    (w - 280, 38), self.FONT, 0.55, self.C_ACCENT2, 1, cv2.LINE_AA)

        # Bottom bar
        self._overlay_rect(frame, 0, h - 50, w, h, (15, 12, 20), 0.6, 0)
        cv2.putText(frame, "ESC: Exit",
                    (20, h - 18), self.FONT, 0.45, self.C_DIM, 1, cv2.LINE_AA)

        if sel_box and two_hands:
            x1, y1, x2, y2 = sel_box
            if pinching:
                cv2.rectangle(frame, (x1, y1), (x2, y2), self.C_RED, 3)
                self._text_center(frame, "CAPTURING...", (y1 + y2) // 2, 1.0, self.C_RED, 2)
            else:
                cv2.rectangle(frame, (x1, y1), (x2, y2), self.C_ACCENT, 2)
                # Corner decorations
                corner_len = 20
                corners = [(x1, y1), (x2, y1), (x1, y2), (x2, y2)]
                dirs = [(1, 1), (-1, 1), (1, -1), (-1, -1)]
                for (cx, cy), (dx, dy) in zip(corners, dirs):
                    cv2.line(frame, (cx, cy), (cx + dx * corner_len, cy), self.C_ACCENT, 3)
                    cv2.line(frame, (cx, cy), (cx, cy + dy * corner_len), self.C_ACCENT, 3)

                # Dimensions label
                pw = x2 - x1
                ph = y2 - y1
                size_text = f"{pw} x {ph}"
                cv2.putText(frame, size_text, (x1 + 5, y1 - 8),
                            self.FONT, 0.5, self.C_ACCENT, 1, cv2.LINE_AA)

        return frame

    # ─────────────────────────── HUD ──────────────────────────────────

    def draw_hud(self, frame, elapsed, moves, hints_left, difficulty_name,
                 shuffling, gesture_label="", open_palm_progress=0.0,
                 thumbs_up_progress=0.0):
        """Top and bottom HUD bars during puzzle gameplay."""
        w, h = self.w, self.h

        # ── Top bar ──
        self._overlay_rect(frame, 0, 0, w, 70, (10, 10, 15), 0.75, 0)

        # Time
        mins = int(elapsed) // 60
        secs = int(elapsed) % 60
        ms = int((elapsed % 1) * 100)
        time_str = f"{mins:02d}:{secs:02d}.{ms:02d}"
        cv2.putText(frame, "TIME", (20, 25), self.FONT, 0.45, self.C_DIM, 1, cv2.LINE_AA)
        cv2.putText(frame, time_str, (20, 55), self.FONT_BOLD, 0.9, self.C_ACCENT, 2, cv2.LINE_AA)

        # Moves
        cv2.putText(frame, "MOVES", (180, 25), self.FONT, 0.45, self.C_DIM, 1, cv2.LINE_AA)
        cv2.putText(frame, str(moves), (180, 55), self.FONT_BOLD, 0.9, self.C_ACCENT2, 2, cv2.LINE_AA)

        # Difficulty
        (dw, _), _ = cv2.getTextSize(difficulty_name, self.FONT_BOLD, 0.7, 2)
        dx = (w - dw) // 2
        cv2.putText(frame, "DIFFICULTY", (dx - 10, 22), self.FONT, 0.4, self.C_DIM, 1, cv2.LINE_AA)
        cv2.putText(frame, difficulty_name, (dx, 52), self.FONT_BOLD, 0.7, self.C_WHITE, 2, cv2.LINE_AA)

        # Hints
        hint_x = w - 200
        cv2.putText(frame, "HINTS", (hint_x, 25), self.FONT, 0.45, self.C_DIM, 1, cv2.LINE_AA)
        for i in range(3):
            color = self.C_GOLD if i < hints_left else (50, 50, 50)
            cv2.circle(frame, (hint_x + i * 28, 48), 10, color, -1)

        # Shuffle indicator
        if shuffling:
            self._text_center(frame, "SHUFFLING...", 55, 0.8, self.C_ACCENT2, 2)

        # ── Bottom bar ──
        self._overlay_rect(frame, 0, h - 70, w, h, (10, 10, 15), 0.75, 0)

        # Gesture hints
        gestures = [
            ("PINCH", "drag tile"),
            ("OPEN PALM", "pause (hold)"),
            ("THUMBS UP", "restart (hold)"),
        ]
        spacing = w // (len(gestures) + 1)
        for i, (g, a) in enumerate(gestures):
            gx = spacing * (i + 1) - 80
            cv2.putText(frame, g, (gx, h - 42), self.FONT_BOLD, 0.5, self.C_ACCENT2, 1, cv2.LINE_AA)
            cv2.putText(frame, a, (gx, h - 20), self.FONT, 0.42, self.C_DIM, 1, cv2.LINE_AA)

        # ── Gesture label feedback ──
        if gesture_label:
            label_y = h - 90
            (lw, lh), _ = cv2.getTextSize(gesture_label, self.FONT_BOLD, 0.7, 2)
            lx = (w - lw) // 2
            self._overlay_rect(frame, lx - 15, label_y - lh - 8,
                               lx + lw + 15, label_y + 8, (30, 60, 30), 0.85)
            cv2.putText(frame, gesture_label, (lx, label_y),
                        self.FONT_BOLD, 0.7, self.C_ACCENT, 2, cv2.LINE_AA)

        # ── Hold-gesture progress arcs ──
        if open_palm_progress > 0.01:
            bar_y = h - 110
            self._text_center(frame, "PAUSE - Hold palm...", bar_y - 16, 0.5, self.C_ACCENT, 1)
            self._progress_bar(frame, (w - 250) // 2, bar_y, 250, 10,
                               open_palm_progress, self.C_ACCENT)

        if thumbs_up_progress > 0.01:
            bar_y = h - 130
            self._text_center(frame, "RESTART - Hold thumb...", bar_y - 16, 0.5, self.C_RED, 1)
            self._progress_bar(frame, (w - 250) // 2, bar_y, 250, 10,
                               thumbs_up_progress, self.C_RED)

        return frame

    def draw_grid(self, frame, x1, y1, x2, y2, rows=3, cols=3):
        cell_w = (x2 - x1) // cols
        cell_h = (y2 - y1) // rows

        for i in range(1, cols):
            cv2.line(frame, (x1 + i * cell_w, y1), (x1 + i * cell_w, y2), (60, 60, 60), 1)

        for i in range(1, rows):
            cv2.line(frame, (x1, y1 + i * cell_h), (x2, y1 + i * cell_h), (60, 60, 60), 1)

        # Outer border
        cv2.rectangle(frame, (x1, y1), (x2, y2), (80, 80, 80), 2)

    # ─────────────────────────── PAUSE SCREEN ─────────────────────────

    def draw_pause(self, frame):
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (self.w, self.h), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)

        self._text_center(frame, "PAUSED", self.h // 2 - 30, 2.0, self.C_ACCENT, 4, self.FONT_SCRIPT)
        self._text_center(frame, "Show THUMBS UP to restart", self.h // 2 + 30, 0.7, self.C_DIM, 1)
        self._text_center(frame, "Show OPEN PALM again to resume", self.h // 2 + 65, 0.7, self.C_DIM, 1)
        return frame

    # ─────────────────────────── WIN SCREEN ───────────────────────────

    def draw_win(self, frame, elapsed, moves, score, difficulty_name, best_score):
        t = self._t()

        # Darken
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (self.w, self.h), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.55, frame, 0.45, 0, frame)

        # Confetti particles
        self._update_confetti(frame)

        # Panel
        px1, py1 = self.w // 2 - 320, self.h // 2 - 220
        px2, py2 = self.w // 2 + 320, self.h // 2 + 240
        self._overlay_rect(frame, px1, py1, px2, py2, (15, 25, 15), 0.88)
        cv2.rectangle(frame, (px1, py1), (px2, py2), self.C_ACCENT, 2)

        # Trophy glow
        glow = 0.5 + 0.5 * math.sin(t * 3)
        glow_color = (int(30 * glow), int(215 * glow), int(255 * glow))
        cv2.putText(frame, "PUZZLE SOLVED!", (self.w // 2 - 220, self.h // 2 - 140),
                    self.FONT_SCRIPT, 1.4, glow_color, 3, cv2.LINE_AA)

        # Stats
        stats = [
            (f"Time: {int(elapsed)//60:02d}:{int(elapsed)%60:02d}.{int((elapsed%1)*100):02d}", self.C_TEXT),
            (f"Moves: {moves}", self.C_TEXT),
            (f"Difficulty: {difficulty_name}", self.C_ACCENT2),
            (f"Score: {score}", self.C_GOLD),
        ]
        for i, (text, color) in enumerate(stats):
            self._text_center(frame, text, self.h // 2 - 60 + i * 55, 0.85, color, 2)

        if best_score > 0:
            self._text_center(frame, f"Best: {best_score}", self.h // 2 + 175,
                              0.65, self.C_DIM, 1)

        # Instructions
        self._text_center(frame, "THUMBS UP  to play again", self.h // 2 + 215,
                          0.6, self.C_ACCENT, 1)

        return frame

    def _init_confetti(self):
        w, h = self.w, self.h
        import random
        self._particles = []
        colors = [
            (80, 220, 130), (30, 215, 255), (220, 160, 40),
            (220, 80, 140), (80, 140, 220), (255, 255, 100)
        ]
        for _ in range(80):
            self._particles.append({
                'x': random.randint(0, w),
                'y': random.randint(-h, 0),
                'vx': random.uniform(-2, 2),
                'vy': random.uniform(3, 8),
                'color': random.choice(colors),
                'size': random.randint(4, 12),
                'shape': random.choice(['rect', 'circle']),
                'angle': random.uniform(0, 360),
                'spin': random.uniform(-5, 5),
            })

    def _update_confetti(self, frame):
        import random
        if not self._particles:
            self._init_confetti()

        for p in self._particles:
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['angle'] += p['spin']
            p['vy'] += 0.1  # gravity

            if p['y'] > self.h + 20:
                p['y'] = random.randint(-100, -10)
                p['x'] = random.randint(0, self.w)
                p['vy'] = random.uniform(3, 8)

            x, y = int(p['x']), int(p['y'])
            s = p['size']
            if 0 <= x < self.w and 0 <= y < self.h:
                if p['shape'] == 'circle':
                    cv2.circle(frame, (x, y), s // 2, p['color'], -1)
                else:
                    cv2.rectangle(frame, (x - s // 2, y - s // 2),
                                  (x + s // 2, y + s // 2), p['color'], -1)

    def reset_confetti(self):
        self._particles = []

    # ─────────────────────────── TRAIL / CURSOR ───────────────────────

    def draw_trail(self, frame, trail_points):
        for i in range(1, len(trail_points)):
            alpha = i / len(trail_points)
            color = (int(80 * alpha), int(220 * alpha), int(130 * alpha))
            thickness = max(1, int(alpha * 4))
            cv2.line(frame, trail_points[i - 1], trail_points[i], color, thickness)

    def draw_cursor(self, frame, cx, cy, pinching, dragging):
        t = self._t()
        if dragging:
            r = 10 + int(3 * math.sin(t * 8))
            cv2.circle(frame, (cx, cy), r + 4, self.C_ACCENT, 1)
            cv2.circle(frame, (cx, cy), r, self.C_ACCENT, -1)
        elif pinching:
            cv2.circle(frame, (cx, cy), 12, self.C_RED, 2)
            cv2.circle(frame, (cx, cy), 5, self.C_RED, -1)
        else:
            cv2.circle(frame, (cx, cy), 8, self.C_WHITE, 1)
            cv2.circle(frame, (cx, cy), 3, self.C_WHITE, -1)