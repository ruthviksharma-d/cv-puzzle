import cv2
import mediapipe as mp
import math
import time


class HandTracker:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.mp_draw = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        self.results = None

        # For gesture debouncing
        self._open_palm_start = None
        self._thumbs_up_start = None
        self._gesture_hold_duration = 1.0  # seconds to hold gesture

    def find_hands(self, frame):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(rgb)

    def draw_hands(self, frame):
        if self.results and self.results.multi_hand_landmarks:
            for handLms in self.results.multi_hand_landmarks:
                self.mp_draw.draw_landmarks(
                    frame, handLms,
                    self.mp_hands.HAND_CONNECTIONS,
                    self.mp_drawing_styles.get_default_hand_landmarks_style(),
                    self.mp_drawing_styles.get_default_hand_connections_style()
                )

    def get_pinch(self):
        if self.results and self.results.multi_hand_landmarks:
            for hand in self.results.multi_hand_landmarks:
                x1, y1 = hand.landmark[4].x, hand.landmark[4].y   # thumb tip
                x2, y2 = hand.landmark[8].x, hand.landmark[8].y   # index tip

                dist = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5

                if dist < 0.05:
                    return True, x2, y2

            hand = self.results.multi_hand_landmarks[0]
            return False, hand.landmark[8].x, hand.landmark[8].y

        return False, 0, 0

    def get_two_fingers(self):
        """Returns index and middle fingertip positions of first hand."""
        if self.results and self.results.multi_hand_landmarks:
            hand = self.results.multi_hand_landmarks[0]
            ix, iy = hand.landmark[8].x, hand.landmark[8].y
            mx, my = hand.landmark[12].x, hand.landmark[12].y
            return True, ix, iy, mx, my
        return False, 0, 0, 0, 0

    def get_two_hand_indices(self):
        """Returns index fingertip positions of both hands."""
        points = []
        if self.results and self.results.multi_hand_landmarks:
            for hand in self.results.multi_hand_landmarks:
                x = hand.landmark[8].x
                y = hand.landmark[8].y
                points.append((x, y))

        if len(points) >= 2:
            return True, points[0], points[1]
        return False, (0, 0), (0, 0)

    def get_index_pos(self):
        """Returns index fingertip of first hand."""
        if self.results and self.results.multi_hand_landmarks:
            hand = self.results.multi_hand_landmarks[0]
            x = hand.landmark[8].x
            y = hand.landmark[8].y
            return True, x, y
        return False, 0, 0

    def get_two_hand_positions(self):
        """Returns list of index fingertip positions for all detected hands."""
        points = []
        if self.results and self.results.multi_hand_landmarks:
            for hand in self.results.multi_hand_landmarks:
                x = hand.landmark[8].x
                y = hand.landmark[8].y
                points.append((x, y))
        return points

    def _is_finger_up(self, hand, tip_id, pip_id):
        """Check if a finger is extended."""
        return hand.landmark[tip_id].y < hand.landmark[pip_id].y

    def _is_thumb_up(self, hand):
        """Check if thumb is up (pointing upward)."""
        tip = hand.landmark[4]
        mcp = hand.landmark[2]
        return tip.y < mcp.y - 0.05

    def detect_open_palm(self):
        """
        Returns (detected: bool, progress: float 0-1).
        Detected=True when user holds open palm for ~1 second.
        """
        if not self.results or not self.results.multi_hand_landmarks:
            self._open_palm_start = None
            return False, 0.0

        hand = self.results.multi_hand_landmarks[0]

        # Check all 4 fingers are extended
        fingers_up = (
            self._is_finger_up(hand, 8, 6) and   # index
            self._is_finger_up(hand, 12, 10) and  # middle
            self._is_finger_up(hand, 16, 14) and  # ring
            self._is_finger_up(hand, 20, 18)       # pinky
        )

        # Check fingers are spread (not curled in)
        index_x = hand.landmark[8].x
        pinky_x = hand.landmark[20].x
        spread = abs(index_x - pinky_x) > 0.08

        if fingers_up and spread:
            if self._open_palm_start is None:
                self._open_palm_start = time.time()
            elapsed = time.time() - self._open_palm_start
            progress = min(elapsed / self._gesture_hold_duration, 1.0)
            if elapsed >= self._gesture_hold_duration:
                self._open_palm_start = None  # reset so it doesn't retrigger immediately
                return True, 1.0
            return False, progress
        else:
            self._open_palm_start = None
            return False, 0.0

    def detect_thumbs_up(self):
        """
        Returns (detected: bool, progress: float 0-1).
        Detected=True when user holds thumbs-up for ~1 second.
        """
        if not self.results or not self.results.multi_hand_landmarks:
            self._thumbs_up_start = None
            return False, 0.0

        hand = self.results.multi_hand_landmarks[0]

        thumb_up = self._is_thumb_up(hand)

        # Other fingers should be curled
        fingers_down = (
            not self._is_finger_up(hand, 8, 6) and
            not self._is_finger_up(hand, 12, 10) and
            not self._is_finger_up(hand, 16, 14) and
            not self._is_finger_up(hand, 20, 18)
        )

        if thumb_up and fingers_down:
            if self._thumbs_up_start is None:
                self._thumbs_up_start = time.time()
            elapsed = time.time() - self._thumbs_up_start
            progress = min(elapsed / self._gesture_hold_duration, 1.0)
            if elapsed >= self._gesture_hold_duration:
                self._thumbs_up_start = None
                return True, 1.0
            return False, progress
        else:
            self._thumbs_up_start = None
            return False, 0.0

    def get_adaptive_smooth_pos(self, prev_x, prev_y, raw_x, raw_y, base_alpha=0.2):
        """Adaptive smoothing: faster when moving fast, slower when near-still."""
        dx = raw_x - prev_x
        dy = raw_y - prev_y
        speed = math.sqrt(dx * dx + dy * dy)

        # Scale alpha based on speed (0..30 pixel range → alpha 0.1..0.5)
        adaptive_alpha = base_alpha + min(speed / 60.0, 0.3)
        new_x = int(adaptive_alpha * raw_x + (1 - adaptive_alpha) * prev_x)
        new_y = int(adaptive_alpha * raw_y + (1 - adaptive_alpha) * prev_y)
        return new_x, new_y