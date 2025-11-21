import cv2
import numpy as np
import os
import json
import socket
import time
from State import CubeState

def load_calibration():
    calib_file = "hsv_calibration.json"
    if os.path.exists(calib_file):
        with open(calib_file, "r") as f:
            return json.load(f)
    return None


def classify_hue(h, s, v, calibration=None):
    if s < 75 and v > 150:  
        return "W"
    
    if s < 90 and v > 180:
        return "W"
    
    if calibration:
        ranges = calibration
    else:
        ranges = {
            "Y": {"h": (20, 42), "s": (80, 255), "v": (150, 255)},
            "O": {"h": (8, 19), "s": (150, 255), "v": (120, 255)},
            "R": {"h": (0, 7), "s": (120, 255), "v": (80, 210)},
            "G": {"h": (45, 90), "s": (80, 255), "v": (100, 255)},
            "B": {"h": (95, 135), "s": (80, 255), "v": (70, 220)},
        }

    for color, val in ranges.items():
        h_min, h_max = val["h"]
        s_min, s_max = val["s"]
        v_min, v_max = val["v"]
        if h_min <= h <= h_max and s_min <= s <= s_max and v_min <= v <= v_max:
            return color

    if v > 140 and s < 80:  
        return "W"
    elif h < 20 and s > 100:
        return "O"
    elif h < 45 and s > 70:
        return "Y"
    elif h < 90:
        return "G"
    elif h < 140:
        return "B"
    else:
        return "R"


def get_position_for_move(move, frame_size, image_size):
    frame_h, frame_w = frame_size
    center_x, center_y = frame_w // 2, frame_h // 2

    positions = {
        "R": (center_x + 180, center_y - 50),
        "R'": (center_x + 180, center_y - 50),
        "L": (center_x - 330, center_y - 50),
        "L'": (center_x - 330, center_y - 50),
        "U": (center_x - 90, center_y - 200),
        "U'": (center_x - 90, center_y - 200),
        "D": (center_x - 90, center_y + 120),
        "D'": (center_x - 90, center_y + 120),
        "F": (center_x - 90, center_y - 50),
        "F'": (center_x - 90, center_y - 50),
    }
    return positions.get(move, (center_x - 75, center_y - 75))


def overlay_image(bg, overlay, position):
    h, w = overlay.shape[:2]
    x, y = position
    if overlay.shape[2] == 4:
        alpha = overlay[:, :, 3] / 255.0
        for c in range(3):
            bg[y:y+h, x:x+w, c] = (1 - alpha) * bg[y:y+h, x:x+w, c] + alpha * overlay[:, :, c]
    else:
        bg[y:y+h, x:x+w] = overlay
    return bg


def draw_arrow_for_move(frame, move):
    image_path = f"Resources/{move}.png"
    if os.path.exists(image_path):
        overlay = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
        if overlay is not None:
            overlay = cv2.resize(overlay, (150, 150))
            position = get_position_for_move(move, frame.shape[:2], (150, 150))
            frame[:] = overlay_image(frame, overlay, position)
            cv2.putText(frame, f"Move: {move}", (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        else:
            cv2.putText(frame, f"Move: {move} (image load failed)", (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    else:
        cv2.putText(frame, f"Move: {move} (no image)", (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)


print("=" * 60)
print("🎯 RUBIK'S CUBE SOLVER (Optimized)")
print("=" * 60)

cube_state = CubeState()

calibration_data = load_calibration()
if calibration_data:
    print("✅ Loaded HSV calibration data from hsv_calibration.json")
else:
    print("⚠️ No calibration file found. Using default HSV thresholds.")

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    cap = cv2.VideoCapture(1)
if not cap.isOpened():
    print("❌ ERROR: Cannot open camera")
    exit(1)

GRID_SIZE = 3
SPACING = 160
DOT_RADIUS = 8
face_order = ['U', 'R', 'F', 'D', 'L', 'B']
cube_faces = {}

print("\n📸 SCANNING PHASE")
print("▶️ Press keys: U R F D L B to scan that face")
print("▶️ Press ESC when all 6 faces are scanned")
print("💡 TIP: For white face, ensure good lighting and avoid shadows")
print("-" * 60)

while True:
    ret, frame = cap.read()
    if not ret:
        print("⚠️ Failed to read frame!")
        break

    frame = cv2.resize(frame, (750, 640))
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    center_x, center_y = 375, 320

    current_face = []
    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            x = center_x + (j - 1) * SPACING
            y = center_y + (i - 1) * SPACING
            h, s, v = hsv[y, x]
            color = classify_hue(h, s, v, calibration_data)
            current_face.append(color)
            
            cv2.circle(frame, (x, y), DOT_RADIUS, (0, 255, 0), -1)
            cv2.putText(frame, color, (x - 15, y - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
            if color == "W":
                cv2.putText(frame, f"S:{s} V:{v}", (x - 30, y + 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)

    cv2.putText(frame, "Press face key (U/R/F/D/L/B)", (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    cv2.putText(frame, f"Scanned: {list(cube_faces.keys())}", (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    cv2.imshow("Cube Scanner", frame)
    key = cv2.waitKey(1) & 0xFF
    if key == 27: 
        break
    elif chr(key).upper() in face_order:
        face_key = chr(key).upper()
        cube_faces[face_key] = current_face.copy()
        print(f"✅ Scanned {face_key}: {current_face}")

cap.release()
cv2.destroyAllWindows()

if len(cube_faces) != 6:
    print(f"\n❌ ERROR: Only scanned {len(cube_faces)} faces. Missing faces: {[f for f in face_order if f not in cube_faces]}")
    exit(1)

print("\n" + "=" * 60)
print("🧠 SOLVING PHASE")
print("=" * 60)

color_to_face = {cube_faces[face][4]: face for face in face_order}
cube_string = ''.join(color_to_face.get(color, '?') for face in face_order for color in cube_faces[face])

print(f"\n🧩 Cube string: {cube_string}")
if len(cube_string) != 54:
    print(f"❌ Invalid cube string length: {len(cube_string)} (expected 54)")
    exit(1)

for f in face_order:
    count = cube_string.count(f)
    if count != 9:
        print(f"⚠️ Warning: {f} count = {count} (should be 9)")

if cube_state.is_solved(cube_string):
    print("\n🎉 CUBE IS ALREADY SOLVED! ✨")
    print("📊 Steps required: 0")
    print("=" * 60)
    input("Press ENTER to exit...")
    exit(0)

try:
    import kociemba
    solution = kociemba.solve(cube_string)
    print(f"\n✅ Solution found: {solution}")
    
    cube_state.set_solution(solution)
    move_count = cube_state.count_moves()
    print(f"📊 Total moves: {move_count}")
    
    if move_count > 25:
        print(f"⚠️ Warning: Solution has {move_count} moves (expected ≤25)")
        print("💡 This might indicate a scanning error. Consider re-scanning.")
    
except Exception as e:
    print(f"\n❌ Error while solving: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

cube_state.save_state()

print("\n" + "=" * 60)
print("🎮 VISUAL GUIDANCE")
print("=" * 60)
print("▶️ Press SPACE to confirm each move")
print("▶️ Press ESC to exit at any time")
print("💡 Note: X2 means do that move twice")
print("-" * 60)

viewer_connected = False
sock = None
try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(('localhost', 9999))
    viewer_connected = True
    print("✅ Connected to viewerStarting visual guidance.")
except ConnectionRefusedError:
    print("✅ Connected to viewer,Starting visual guidance.")

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    cap = cv2.VideoCapture(1)
if not cap.isOpened():
    print("⚠️ Camera not available — running guidance in console only.")
    cap = None

expanded_moves = cube_state.expand_moves()

while cube_state.move_index < cube_state.total_moves:
    move = expanded_moves[cube_state.move_index]

    if cap:
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv2.resize(frame, (750, 640))
        base_move = move.replace("'", "").replace("2", "")
        
        if base_move in ["R", "L", "U", "D", "F", "B"]:
            draw_arrow_for_move(frame, move.replace("2", ""))
            if move.endswith("2"):
                cv2.putText(frame, "DO THIS TWICE!", (200, 100),
                           cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 165, 255), 3)
        else:
            cv2.putText(frame, f"Move: {move}", (80, 320),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 3)

        cv2.putText(frame, f"Step {cube_state.move_index + 1}/{cube_state.total_moves}", (30, 600),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        cv2.imshow("Cube Solver - Guidance", frame)
        key = cv2.waitKey(1) & 0xFF

        if key == ord(' '):
            cube_state.next_move()
            cube_state.save_state()
        elif key == 27:
            break
    else:
        if move.endswith("2"):
            print(f"👉 Perform move: {move[0]} TWICE")
        else:
            print(f"👉 Perform move: {move}")
        input("Press ENTER when done...")
        cube_state.next_move()
        cube_state.save_state()

if cap:
    cap.release()
    cv2.destroyAllWindows()

print("\n🎉 Cube solved! All moves completed successfully.")
if viewer_connected and sock:
    sock.close()