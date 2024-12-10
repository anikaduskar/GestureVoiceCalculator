import threading
import queue
import cv2
import time
import numpy as np
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtCore import QTimer
from mediapipe import solutions as mp_solutions
from gui import CalculatorGUI
from voice_module import VoiceRecognizer

# Globals to manage the state of the application
stop_threads = False  # Signals threads to stop gracefully when the app closes
command_queue = queue.Queue()  # Queue for communication between the detection thread and GUI
gesture_detection_active = False  # Keeps track of whether gesture detection is active
current_phase = "select_number"  # Tracks current phase: "select_number", "select_operator", "evaluate"
selected_expression = []  # Holds the current mathematical expression
selection_buffer_time = 2  # Minimum time between valid selections (in seconds)
last_selection_time = 0  # Timestamp of the last valid selection
bubble_radius = 45  # Radius of the interaction bubbles displayed on the webcam feed

# Number Bubble Display 
def display_number_bubbles(frame):
    height, width, _ = frame.shape
    center_x, center_y = width // 2, height // 2  # Center of the frame

    # Offset values for bubble positions relative to the center
    offset_x = width * 0.20
    offset_y = height * 0.20

    # Define positions for numbers and the transition arrow
    number_positions = [
        (int(center_x - offset_x), int(center_y - offset_y)),  # Top-left
        (int(center_x), int(center_y - offset_y)),            # Top-center
        (int(center_x + offset_x), int(center_y - offset_y)), # Top-right
        (int(center_x - offset_x), int(center_y)),            # Middle-left
        (int(center_x), int(center_y)),                      # Center
        (int(center_x + offset_x), int(center_y)),            # Middle-right
        (int(center_x - offset_x), int(center_y + offset_y)), # Bottom-left
        (int(center_x), int(center_y + offset_y)),            # Bottom-center
        (int(center_x + offset_x), int(center_y + offset_y)), # Bottom-right
        (int(center_x), int(center_y + (2 * offset_y)))       # Bottom-center for "0"
    ]
    arrow_position = (int(center_x + (2 * offset_x)), int(center_y))  # Arrow bubble on the right

    # Defining number labels
    numbers = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"]

    # Adding the number bubbles
    for i, pos in enumerate(number_positions):
        cv2.circle(frame, pos, bubble_radius, (52, 152, 219), -1) 
        text_size = cv2.getTextSize(numbers[i], cv2.FONT_HERSHEY_DUPLEX, 1.4, 3)[0]
        text_x = pos[0] - text_size[0] // 2
        text_y = pos[1] + text_size[1] // 2
        cv2.putText(frame, numbers[i], (text_x, text_y),
                    cv2.FONT_HERSHEY_DUPLEX, 1.8, (255, 255, 255), 3)  

    # Adding the arrow bubble
    cv2.circle(frame, arrow_position, bubble_radius, (241, 196, 15), -1)  
    arrow_text = "->"
    text_size = cv2.getTextSize(arrow_text, cv2.FONT_HERSHEY_DUPLEX, 1.4, 3)[0]
    text_x = arrow_position[0] - text_size[0] // 2
    text_y = arrow_position[1] + text_size[1] // 2
    cv2.putText(frame, arrow_text, (text_x, text_y),
                cv2.FONT_HERSHEY_DUPLEX, 1.4, (255, 255, 255), 3)  

    return number_positions, numbers, arrow_position

# Operator Bubble Display 
def display_operator_bubbles(frame):
    height, width, _ = frame.shape
    center_x, center_y = width // 2, height // 2  # Center of the frame
    offset = height * 0.15  # Offset for operator positions

    # Define positions for operators
    operator_positions = [
        (int(center_x - offset), int(center_y)),            # Left
        (int(center_x + offset), int(center_y)),            # Right
        (int(center_x), int(center_y - offset)),            # Top
        (int(center_x), int(center_y + offset)),            # Bottom
        (int(center_x), int(center_y + (2 * offset) + 20))  # "=" positioned slightly lower
    ]
    operators = ["+", "-", "*", "/", "="]

    # Adding the operator bubbles
    for i, pos in enumerate(operator_positions):
        color = (231, 76, 60) if operators[i] == "=" else (46, 204, 113)  
        cv2.circle(frame, pos, bubble_radius, color, -1)
        text_size = cv2.getTextSize(operators[i], cv2.FONT_HERSHEY_DUPLEX, 1.4, 3)[0]
        text_x = pos[0] - text_size[0] // 2
        text_y = pos[1] + text_size[1] // 2
        cv2.putText(frame, operators[i], (text_x, text_y),
                    cv2.FONT_HERSHEY_DUPLEX, 1.4, (255, 255, 255), 3) 

    return operator_positions, operators

# Gesture Detection 
def run_gesture_detection():
    global stop_threads, gesture_detection_active, current_phase, selected_expression, last_selection_time

    # Initializing MediaPipe's hand detection model
    hands = mp_solutions.hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7) #70% confidence model
    cap = cv2.VideoCapture(0)  # Open the webcam

    if not cap.isOpened():
        print("Error: Unable to access the webcam.")
        return

    try:
        while not stop_threads:
            ret, frame = cap.read()
            if not ret:
                break

            if gesture_detection_active:
                # Flipping and resizing the frame for consistent interaction
                frame = cv2.flip(frame, 1)
                frame = cv2.resize(frame, (775, 500))
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # Converting to RGB for MediaPipe
                results = hands.process(rgb_frame)  # Detecting hands

                # Getting the fingertip position
                index_tip = None
                if results.multi_hand_landmarks:
                    for hand_landmarks in results.multi_hand_landmarks:
                        index_tip = hand_landmarks.landmark[mp_solutions.hands.HandLandmark.INDEX_FINGER_TIP]
                        x, y = int(index_tip.x * frame.shape[1]), int(index_tip.y * frame.shape[0])
                        cv2.circle(frame, (x, y), 7, (0, 0, 255), -1)  # Red pointer for the fingertip

                # Handling current phase
                if current_phase == "select_number":
                    positions, labels, arrow_position = display_number_bubbles(frame)
                    if index_tip:
                        for i, pos in enumerate(positions):
                            if abs(pos[0] - x) < bubble_radius and abs(pos[1] - y) < bubble_radius: #Finding nearest number bubble
                                if time.time() - last_selection_time > selection_buffer_time:
                                    selected_expression.append(labels[i])
                                    command_queue.put(("".join(selected_expression), "gesture"))
                                    last_selection_time = time.time()
                                    break
                        # Transitioning to operator phase if arrow is selected
                        if abs(arrow_position[0] - x) < bubble_radius and abs(arrow_position[1] - y) < bubble_radius:
                            if time.time() - last_selection_time > selection_buffer_time:
                                current_phase = "select_operator"
                                last_selection_time = time.time()

                elif current_phase == "select_operator":
                    positions, labels = display_operator_bubbles(frame)
                    if index_tip:
                        for i, pos in enumerate(positions):
                            if abs(pos[0] - x) < bubble_radius and abs(pos[1] - y) < bubble_radius:
                                if time.time() - last_selection_time > selection_buffer_time:
                                    if labels[i] == "=":  # Evaluate expression on "=" selection
                                        result = evaluate_expression("".join(selected_expression))
                                        command_queue.put((result, "gesture"))
                                        selected_expression = []  # Reset the expression
                                        current_phase = "select_number"  # Reset to number phase
                                    else:
                                        selected_expression.append(labels[i])
                                        command_queue.put(("".join(selected_expression), "gesture"))
                                        current_phase = "select_number"
                                    last_selection_time = time.time()
                                    break

                command_queue.put((frame, "frame"))  # Send the updated frame to the queue
    finally:
        cap.release()
        print("Webcam released and thread exited.")

# Expression Evaluation 
def evaluate_expression(expression):
    try:
        result = eval(expression)
        return f"{expression} = {result}"
    except ZeroDivisionError:
        return "Error: Division by Zero"
    except Exception as e:
        print(f"Error evaluating expression: {e}")
        return "Error: Invalid expression"

# Voice Command Parsing ---
def parse_voice_command(command):
    number_words = {
        "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4,
        "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9,
    }

    words = command.lower().split()
    for i, word in enumerate(words):
        if word in number_words:
            words[i] = str(number_words[word])
    command = " ".join(words)

    try:
        numbers = [int(s) for s in command.split() if s.isdigit()]
        if "add" in command:
            return f"{' + '.join(map(str, numbers))}"
        elif "subtract" in command:
            return f"{' - '.join(map(str, numbers))}"
        elif "multiply" in command:
            return f"{' * '.join(map(str, numbers))}"
        elif "divide" in command:
            return f"{' / '.join(map(str, numbers))}"
        else:
            return f"Error: Unrecognized operation in command: '{command}'"
    except Exception as e:
        print(f"Error parsing voice command: {e}")
    return "Error: Command not recognized"

# Application Entry Point 
if __name__ == "__main__":
    gesture_thread = threading.Thread(target=run_gesture_detection, daemon=True)  # Start the gesture detection thread
    gesture_thread.start()

    app = QApplication([])
    calculator = CalculatorGUI()
    current_expression = ""
    voice_result = ""

    def process_queue():
        global current_expression
        while not command_queue.empty():
            command, cmd_type = command_queue.get()
            if cmd_type == "gesture" and gesture_detection_active:
                calculator.update_expression(command)
            elif cmd_type == "frame" and gesture_detection_active:
                frame = command
                frame_resized = cv2.resize(frame, (800, 500))  # Resizing the frame for GUI
                frame_rgb = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB)
                height, width, channel = frame_rgb.shape
                bytes_per_line = 3 * width
                q_image = QImage(frame_rgb.data, width, height, bytes_per_line, QImage.Format_RGB888)
                calculator.update_webcam_feed(QPixmap.fromImage(q_image))

    timer = QTimer()
    timer.timeout.connect(process_queue)  # Calling process_queue periodically
    timer.start(100)  # Interval of 100ms

    def activate_voice_logic(): #Calls the recognize_voice function from the voice module
        global voice_result
        voice_recognizer = VoiceRecognizer()
        command = voice_recognizer.recognize_voice()
        if command:
            expression = parse_voice_command(command)
            if "Error" not in expression:
                voice_result = evaluate_expression(expression)
                calculator.update_expression(voice_result)
            else:
                voice_result = expression
                calculator.update_expression(voice_result)

    def toggle_gesture_detection():
        global gesture_detection_active
        gesture_detection_active = not gesture_detection_active
        state = "enabled" if gesture_detection_active else "disabled"
        print(f"Gesture detection {state}.")

    def clear_expression(): #Clears the expression generated till now
        global selected_expression, current_phase
        selected_expression = []  # Reset the expression buffer
        current_phase = "select_number"  # Reset to the initial phase
        calculator.update_expression("")  # Clear the display
        print("Expression cleared.")

    # Connecting the GUI buttons to their respective logic
    calculator.voice_button.clicked.connect(activate_voice_logic)
    calculator.gesture_button.clicked.connect(toggle_gesture_detection)
    calculator.clear_button.clicked.connect(clear_expression)

    calculator.show()
    app.exec()

    # Ensuring threads stop when the application exits
    stop_threads = True
    gesture_thread.join()
    print("Gesture recognition thread terminated.")
