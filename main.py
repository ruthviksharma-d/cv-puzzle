import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

import cv2
import time
import numpy as np

from hand_tracker import HandTracker
from puzzle import Puzzle
from ui_manager import UIManager
from game_manager import GameManager

# ═══════════════════════ PRELOADED IMAGES ═══════════════════════════
# Drop any .jpg/.png into the same folder and add the path here
PRELOADED_IMAGES = [
    "sample1.jpg",
    "sample2.jpg",
    "sample3.jpg",
]

# ═══════════════════════ CAMERA SETUP ═══════════════════════════════
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

ret, test_frame = cap.read()
W = test_frame.shape[1] if ret else 1280
H = test_frame.shape[0] if ret else 720

cv2.namedWindow("Gesture Puzzle", cv2.WINDOW_NORMAL)
cv2.setWindowProperty("Gesture Puzzle", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

# ═══════════════════════ SUBSYSTEMS ═════════════════════════════════
tracker  = HandTracker()
puzzle   = Puzzle(3)
ui       = UIManager(W, H)
gm       = GameManager()

gm.go_menu()

# ═══════════════════════ HELPERS ════════════════════════════════════

def inside_box(px, py, x1, y1, x2, y2, w, h):
    fx, fy = px * w, py * h
    return x1 <= fx <= x2 and y1 <= fy <= y2

def to_local(px, py, x1, y1, x2, y2, w, h):
    fx, fy = px * w, py * h
    if fx < x1 or fx > x2 or fy < y1 or fy > y2:
        return None
    return (fx - x1) / (x2 - x1), (fy - y1) / (y2 - y1)

def load_preloaded_image(grid_size, w, h):
    """Try to load a preloaded sample image, fallback to generated."""
    for path in PRELOADED_IMAGES:
        if os.path.exists(path):
            img = cv2.imread(path)
            if img is not None:
                img = cv2.resize(img, (w, h))
                return img
    # Fallback: generate a colorful gradient image
    img = np.zeros((h, w, 3), dtype=np.uint8)
    for y in range(h):
        for x in range(w):
            img[y, x] = [
                int(180 * x / w + 30),
                int(120 * y / h + 60),
                int(200 * (1 - x / w) + 20)
            ]
    # Add some grid lines for visual interest
    step = w // 8
    for i in range(0, w, step):
        cv2.line(img, (i, 0), (i, h), (200, 200, 200), 1)
    for i in range(0, h, step):
        cv2.line(img, (0, i), (w, i), (200, 200, 200), 1)
    cv2.putText(img, "No image found", (w//2 - 120, h//2),
                cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)
    cv2.putText(img, "Add sample1.jpg etc.", (w//2 - 140, h//2 + 40),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 200), 1)
    return img

# ═══════════════════════ MAIN LOOP ══════════════════════════════════
while True:
    ret, frame = cap.read()
    if not ret:
        continue

    frame = cv2.flip(frame, 1)
    output = frame.copy()

    tracker.find_hands(frame)

    # ── Common gesture reads ──
    pinch, px, py       = tracker.get_pinch()
    detected, ix, iy    = tracker.get_index_pos()
    two_hands, p1, p2   = tracker.get_two_hand_indices()

    # Smooth cursor
    if detected:
        raw_cx = int(ix * W)
        raw_cy = int(iy * H)
        gm.smooth_x, gm.smooth_y = tracker.get_adaptive_smooth_pos(
            gm.smooth_x, gm.smooth_y, raw_cx, raw_cy
        )

    # ════════════════════════════════════════
    #              MENU MODE
    # ════════════════════════════════════════
    if gm.mode == "menu":
        open_palm, palm_prog = tracker.detect_open_palm()

        ui.draw_main_menu(output, gm.selected_diff, gm.diff_names,
                          gm.image_source, gm.IMAGE_SOURCES, palm_prog)

        if detected:
            ui.draw_menu_cursor(output, gm.smooth_x, gm.smooth_y, pinch)

        # Pinch to select difficulty/source
        if pinch and not gm.prev_pinch and detected:
            gm.menu_pinch_action(gm.smooth_x, gm.smooth_y, W, H)

        # Open palm to start
        if open_palm:
            puzzle = Puzzle(gm.grid_size)
            if gm.image_source == 0:
                # Camera mode next
                gm.go_camera()
            else:
                # Preloaded image
                pw = int(W * 0.7)
                ph = int(H * 0.7)
                x1 = (W - pw) // 2
                y1 = (H - ph) // 2
                img = load_preloaded_image(gm.grid_size, pw, ph)
                puzzle.create(img)
                gm.go_puzzle(x1, y1, x1 + pw, y1 + ph)
                ui.reset_confetti()

        gm.prev_pinch = pinch

    # ════════════════════════════════════════
    #            CAMERA MODE
    # ════════════════════════════════════════
    elif gm.mode == "camera":
        sel_box = None

        if two_hands:
            x1 = int(p1[0] * W)
            y1 = int(p1[1] * H)
            x2 = int(p2[0] * W)
            y2 = int(p2[1] * H)
            x1, x2 = min(x1, x2), max(x1, x2)
            y1, y2 = min(y1, y2), max(y1, y2)
            sel_box = (x1, y1, x2, y2)

            if pinch and not gm.prev_pinch:
                if abs(x2 - x1) > 100 and abs(y2 - y1) > 100:
                    crop = frame[y1:y2, x1:x2]
                    if crop.size != 0:
                        puzzle.create(crop)
                        gm.go_puzzle(x1, y1, x2, y2)
                        ui.reset_confetti()

        tracker.draw_hands(output)
        ui.draw_camera_ui(output, two_hands, sel_box, pinch)
        gm.prev_pinch = pinch

    # ════════════════════════════════════════
    #            PUZZLE MODE
    # ════════════════════════════════════════
    elif gm.mode == "puzzle":

        # ── Render puzzle tiles ──
        if gm.sel_x1 is not None:
            puzzle_img = puzzle.combine()
            puzzle_img = cv2.resize(puzzle_img, (gm.sel_x2 - gm.sel_x1, gm.sel_y2 - gm.sel_y1))
            output[gm.sel_y1:gm.sel_y2, gm.sel_x1:gm.sel_x2] = puzzle_img
            ui.draw_grid(output, gm.sel_x1, gm.sel_y1, gm.sel_x2, gm.sel_y2,
                         gm.grid_size, gm.grid_size)

        # ── Shuffle animation ──
        gm.update_shuffle(puzzle)

        # ── Elapsed time ──
        if gm.start_time and not gm.shuffling:
            gm.elapsed = time.time() - gm.start_time

        # ── Special gestures (pause / restart) ──
        open_palm, palm_prog = tracker.detect_open_palm()
        thumbs_up, thumb_prog = tracker.detect_thumbs_up()

        if open_palm:
            gm.go_paused()

        if thumbs_up:
            gm.set_gesture_label("RESTARTING...")
            # Rebuild same puzzle config
            puzzle = Puzzle(gm.grid_size)
            if gm.image_source == 0 and gm.sel_x1 is not None:
                crop = frame[gm.sel_y1:gm.sel_y2, gm.sel_x1:gm.sel_x2]
                if crop.size != 0:
                    puzzle.create(crop)
                    gm.go_puzzle(gm.sel_x1, gm.sel_y1, gm.sel_x2, gm.sel_y2)
            else:
                pw = gm.sel_x2 - gm.sel_x1
                ph = gm.sel_y2 - gm.sel_y1
                img = load_preloaded_image(gm.grid_size, pw, ph)
                puzzle.create(img)
                gm._begin_shuffle()
                gm.start_time = None
                gm.solved = False
                gm.end_time = None
                ui.reset_confetti()

        # ── Cursor smoothing + trail ──
        if detected and gm.sel_x1 is not None:
            cx = max(gm.sel_x1, min(gm.smooth_x, gm.sel_x2))
            cy = max(gm.sel_y1, min(gm.smooth_y, gm.sel_y2))
            gm.smooth_x, gm.smooth_y = cx, cy

            if pinch and inside_box(ix, iy, gm.sel_x1, gm.sel_y1, gm.sel_x2, gm.sel_y2, W, H):
                gm.trail.append((gm.smooth_x, gm.smooth_y))
                if len(gm.trail) > 20:
                    gm.trail.pop(0)

            # Hover tile
            local = to_local(ix, iy, gm.sel_x1, gm.sel_y1, gm.sel_x2, gm.sel_y2, W, H)
            if local:
                gm.hover_tile = puzzle.get_index(local[0], local[1])
            else:
                gm.hover_tile = None

        # ── Tile interaction (drag & drop) ──
        if not gm.shuffling:
            # Hover effect
            if gm.hover_tile is not None and gm.sel_x1 is not None:
                puzzle.draw_hover(output, gm.sel_x1, gm.sel_y1, gm.sel_x2, gm.sel_y2, gm.hover_tile)

            # Pick up tile
            if pinch and not gm.prev_pinch:
                if (gm.sel_x1 is not None and
                        inside_box(px, py, gm.sel_x1, gm.sel_y1, gm.sel_x2, gm.sel_y2, W, H)):
                    local = to_local(px, py, gm.sel_x1, gm.sel_y1, gm.sel_x2, gm.sel_y2, W, H)
                    if local:
                        lx, ly = local
                        puzzle.selected = puzzle.get_index(lx, ly)
                        gm.dragging = True
                        gm.set_gesture_label("Dragging tile", 0.5)

            # Drop tile
            elif not pinch and gm.prev_pinch:
                if gm.dragging and puzzle.selected is not None:
                    if gm.sel_x1 is not None:
                        local = to_local(px, py, gm.sel_x1, gm.sel_y1, gm.sel_x2, gm.sel_y2, W, H)
                        if local:
                            lx, ly = local
                            idx2 = puzzle.get_index(lx, ly)
                            puzzle.swap(puzzle.selected, idx2)

                    gm.trail = []
                    gm.dragging = False
                    puzzle.selected = None

                    # Check win
                    if gm.start_time is not None and not gm.solved:
                        if puzzle.is_solved():
                            gm.solved = True
                            gm.cache_moves(puzzle)
                            gm.go_won(gm.elapsed)

        gm.prev_pinch = pinch

        # ── Draw overlays ──
        if gm.sel_x1 is not None:
            puzzle.draw_selected(output, gm.sel_x1, gm.sel_y1, gm.sel_x2, gm.sel_y2)
            puzzle.draw_hint(output, gm.sel_x1, gm.sel_y1, gm.sel_x2, gm.sel_y2)

        ui.draw_trail(output, gm.trail)

        if detected:
            ui.draw_cursor(output, gm.smooth_x, gm.smooth_y, pinch, gm.dragging)

        tracker.draw_hands(output)

        ui.draw_hud(output, gm.elapsed, puzzle.move_count, puzzle.hints_remaining,
                    gm.diff_name, gm.shuffling, gm.get_gesture_label(),
                    palm_prog, thumb_prog)

    # ════════════════════════════════════════
    #            PAUSED MODE
    # ════════════════════════════════════════
    elif gm.mode == "paused":
        if gm.sel_x1 is not None:
            puzzle_img = puzzle.combine()
            puzzle_img = cv2.resize(puzzle_img, (gm.sel_x2 - gm.sel_x1, gm.sel_y2 - gm.sel_y1))
            output[gm.sel_y1:gm.sel_y2, gm.sel_x1:gm.sel_x2] = puzzle_img

        ui.draw_pause(output)

        # Resume on open palm
        open_palm, palm_prog = tracker.detect_open_palm()
        thumbs_up, thumb_prog = tracker.detect_thumbs_up()

        if open_palm:
            gm.go_resume()

        if thumbs_up:
            # Restart whole puzzle
            gm.go_menu()

        tracker.draw_hands(output)

    # ════════════════════════════════════════
    #              WON MODE
    # ════════════════════════════════════════
    elif gm.mode == "won":
        if gm.sel_x1 is not None:
            puzzle_img = puzzle.combine()
            puzzle_img = cv2.resize(puzzle_img, (gm.sel_x2 - gm.sel_x1, gm.sel_y2 - gm.sel_y1))
            output[gm.sel_y1:gm.sel_y2, gm.sel_x1:gm.sel_x2] = puzzle_img

        ui.draw_win(output, gm.elapsed, gm._move_count, gm.score,
                    gm.diff_name, gm.best_scores[gm.selected_diff])

        # Thumbs up → go back to menu
        thumbs_up, thumb_prog = tracker.detect_thumbs_up()
        if thumbs_up:
            gm.go_menu()

        tracker.draw_hands(output)

    # ════════════════════════════════════════
    cv2.imshow("Gesture Puzzle", output)

    key = cv2.waitKey(1) & 0xFF
    if key == 27:  # ESC
        break
    elif key == ord('m'):  # 'm' → back to menu
        gm.go_menu()
    elif key == ord('h'):  # 'h' → hint (keyboard fallback)
        if gm.mode == "puzzle" and not gm.shuffling:
            puzzle.activate_hint()

cap.release()
cv2.destroyAllWindows()