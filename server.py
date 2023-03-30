import socket
import json
import time
import keyboard
import ctypes
import sys
from typing import List
import pickle

if sys.platform == 'win32':
    from ctypes import windll
else:
    print("This script is designed to work on Windows. Exiting.")
    sys.exit(1)

# Load config
with open("config.json") as config_file:
    config = json.load(config_file)

# Key mapping
key_mapping = {
    0: 'space',      # X button
    1: 'c',      # Circle button
    2: 'f',      # Square button
    3: 'e',        # Triangle button
    4: 'q',          # L1 button
    5: 'shift',          # R1 button
    6: 'tab',          # Share button
    7: 'esc',          # Options button
    8: 'ctrl',        # L3
    9: 't',          # R3
    # 10: 'z',         # L3 button (left stick press)
    # 11: 'x',         # R3 button (right stick press)
    # 12: 'c',         # PS button
    # 13: 'v',         # Touchpad button
}

# Trigger mapping
trigger_mapping = {
    # 'left': 'left_mouse',
    'left' : 'right_mouse',
    'right': 'left_mouse',
}

# D-pad mapping
dpad_mapping = {
    (-1, 0): 'left_arrow',  # Left D-pad button
    (1, 0): 'right_arrow',  # Right D-pad button
    (0, -1): 'down_arrow',  # Down D-pad button
    (0, 1): 'up_arrow',  # Up D-pad button
}

button_combination_mapping = {
    (4, 2): 'x',  # L1 and Square buttons together
}

# Initialize server socket
server_address = (config["server_ip"], config["server_port"])
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(server_address)
server_socket.listen(1)

print("Server is listening on {}:{}".format(*server_address))

# Wait for a client to connect
client_socket, client_address = server_socket.accept()
print("Client connected from {}:{}".format(*client_address))

# Other variables
pressed_keys = set()
joystick_deadzone = 0.2
mouse_sensitivity = 20
trigger_threshold = 0.5

# Windows API mouse input structure
class MOUSEINPUT(ctypes.Structure):
    _fields_ = [("dx", ctypes.c_long),
                ("dy", ctypes.c_long),
                ("mouseData", ctypes.c_ulong),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong))]

class INPUT(ctypes.Structure):
    _fields_ = [("type", ctypes.c_ulong),
                ("mi", MOUSEINPUT)]


# Import Windows API functions
# ... (continued from above)

# Import Windows API functions
SendInput = ctypes.windll.user32.SendInput
MOUSEEVENTF_MOVE = 0x0001
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
MOUSEEVENTF_RIGHTDOWN = 0x0008
MOUSEEVENTF_RIGHTUP = 0x0010
INPUT_MOUSE = 0

# Function to simulate mouse actions using Windows API
def mouse_action(dx=None, dy=None, left_down=False, left_up=False, right_down=False, right_up=False):
    flags = 0
    if dx is not None and dy is not None:
        flags |= MOUSEEVENTF_MOVE
    if left_down:
        flags |= MOUSEEVENTF_LEFTDOWN
    if left_up:
        flags |= MOUSEEVENTF_LEFTUP
    if right_down:
        flags |= MOUSEEVENTF_RIGHTDOWN
    if right_up:
        flags |= MOUSEEVENTF_RIGHTUP

    mouse_info = MOUSEINPUT(dx or 0, dy or 0, 0, flags, 0, None)
    mouse_input = INPUT(INPUT_MOUSE, mouse_info)
    SendInput(1, ctypes.pointer(mouse_input), ctypes.sizeof(mouse_input))


def trigger_action(trigger, pressed):
    if trigger in ['left_mouse', 'right_mouse']:
        if trigger == 'left_mouse':
            mouse_action(left_down=pressed, left_up=not pressed)
        elif trigger == 'right_mouse':
            mouse_action(right_down=pressed, right_up=not pressed)
    else:
        print(trigger)
        if pressed and trigger not in pressed_keys:
            keyboard.press(trigger)
            pressed_keys.add(trigger)
        elif not pressed and trigger in pressed_keys:
            keyboard.release(trigger)
            pressed_keys.remove(trigger)

# Function to process controller data
def process_controller_data(controller_data: dict, pressed_keys: set):
    current_pressed_buttons = set()
    for button, key in key_mapping.items():
        key_state = controller_data["buttons"][button]
        if key_state:
            current_pressed_buttons.add(button)
        else:
            if button in current_pressed_buttons:
                current_pressed_buttons.remove(button)

    # Check for button combinations
    for button_combo, key in button_combination_mapping.items():
        if all(button in current_pressed_buttons for button in button_combo):
            if key not in pressed_keys:
                print(f"Button combination {button_combo} pressed")  # Modified print statement
                keyboard.press(key)
                pressed_keys.add(key)
        elif key in pressed_keys:
            print(f"Button combination {button_combo} released")  # Added print statement
            keyboard.release(key)
            pressed_keys.remove(key)

    # Press and release single button keybinds
    for button, key in key_mapping.items():
        key_state = controller_data["buttons"][button]
        current_key_state = key in pressed_keys

        combo_key_used = False
        for combo, combo_key in button_combination_mapping.items():
            if button in combo:
                if all(b in current_pressed_buttons for b in combo):
                    combo_key_used = True
                    break

        if key_state and not current_key_state:
            if not combo_key_used:
                print(f"{key} pressed")  # Modified print statement
                keyboard.press(key)
                pressed_keys.add(key)
            elif combo_key_used and all(b not in current_pressed_buttons for b in combo):
                keyboard.release(combo_key)
                pressed_keys.remove(combo_key)

        elif not key_state and current_key_state and not combo_key_used:
            print(f"{key} released")  # Modified print statement
            keyboard.release(key)
            pressed_keys.remove(key)


    # ... (rest of the code using controller_data instead of joystick)


        # Left analog stick
        left_x_axis = controller_data["axes"][0]
        left_y_axis = controller_data["axes"][1]
        
        if left_x_axis > joystick_deadzone:
            if 'd' not in pressed_keys:
                keyboard.press('d')
                pressed_keys.add('d')
        else:
            if 'd' in pressed_keys:
                keyboard.release('d')
                pressed_keys.remove('d')

        if left_x_axis < -joystick_deadzone:
            if 'a' not in pressed_keys:
                keyboard.press('a')
                pressed_keys.add('a')
        else:
            if 'a' in pressed_keys:
                keyboard.release('a')
                pressed_keys.remove('a')

        if left_y_axis > joystick_deadzone:
            if 's' not in pressed_keys:
                keyboard.press('s')
                pressed_keys.add('s')
        else:
            if 's' in pressed_keys:
                keyboard.release('s')
                pressed_keys.remove('s')

        if left_y_axis < -joystick_deadzone:
            if 'w' not in pressed_keys:
                keyboard.press('w')
                pressed_keys.add('w')
        else:
            if 'w' in pressed_keys:
                keyboard.release('w')
                pressed_keys.remove('w')


        # Right analog stick for mouse movement
        right_x_axis = controller_data["axes"][2]
        right_y_axis = controller_data["axes"][3]

        if abs(right_x_axis) > joystick_deadzone or abs(right_y_axis) > joystick_deadzone:
            dx = int(right_x_axis * mouse_sensitivity)
            dy = int(right_y_axis * mouse_sensitivity)
            mouse_action(dx, dy)

        # D-pad inputs
        hat_value = controller_data["hats"][0]
        for dpad_direction, dpad_key in dpad_mapping.items():
            key_state = hat_value == dpad_direction
            current_key_state = dpad_key in pressed_keys

            if key_state and not current_key_state:
                print(dpad_key)
                keyboard.press(dpad_key)
                pressed_keys.add(dpad_key)
            elif not key_state and current_key_state:
                keyboard.release(dpad_key)
                pressed_keys.remove(dpad_key)


        # Trigger buttons
        left_trigger = controller_data["axes"][4]
        right_trigger = controller_data["axes"][5]

        # Left trigger (aim)
        if left_trigger > trigger_threshold and not trigger_states['left_mouse']:
            trigger_states['left_mouse'] = True
            trigger_action(trigger_mapping['left'], True)
        elif left_trigger <= trigger_threshold and trigger_states['left_mouse']:
            trigger_states['left_mouse'] = False
            trigger_action(trigger_mapping['left'], False)

        # Right trigger (shoot)
        if right_trigger > trigger_threshold and not trigger_states['right_mouse']:
            trigger_states['right_mouse'] = True
            trigger_action(trigger_mapping['right'], True)
        elif right_trigger <= trigger_threshold and trigger_states['right_mouse']:
            trigger_states['right_mouse'] = False
            trigger_action(trigger_mapping['right'], False)

invalid_data_file = open("invalid_data.txt", "a")


try:
    trigger_states = {'left_mouse': False, 'right_mouse': False}

    while True:
        try:
            received_data = client_socket.recv(1024)

            # Split the data by newline character
            data_parts = received_data.split(b'\n')

            for data_part in data_parts:
                # Skip empty parts
                if not data_part:
                    continue

                # Deserialize the data using json.loads()
                deserialized_data = json.loads(data_part.decode())

                # Access the buttons, axes, and hats data
                button_data = deserialized_data["buttons"]
                axis_data = deserialized_data["axes"]
                hat_data = deserialized_data["hats"]

                # Process controller data
                process_controller_data(deserialized_data, pressed_keys)

            time.sleep(0.01)

        except (json.JSONDecodeError) as e:
            print("Invalid load key encountered, skipping this iteration")
            invalid_data_file.write(f"{e}: {received_data}\n")
            continue
except KeyboardInterrupt:
    print("Exiting...")



# Close the sockets
client_socket.close()
server_socket.close()

