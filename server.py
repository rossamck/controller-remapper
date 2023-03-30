import socket
import json
import time
import threading
import keyboard
import ctypes

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

# Set joystick deadzone
joystick_deadzone = 0.2
mouse_sensitivity = 20
trigger_threshold = 0.5


pressed_keys = set()


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



current_pressed_buttons = set()

def keyPress(joystick_state):
    global current_pressed_buttons

    # Button inputs
    new_pressed_buttons = set()
    for button, key in key_mapping.items():
        key_state = joystick_state['buttons'][button]
        if key_state:
            new_pressed_buttons.add(button)

    pressed_buttons_diff = new_pressed_buttons.symmetric_difference(current_pressed_buttons)
    for button in pressed_buttons_diff:
        key = key_mapping[button]
        if button in new_pressed_buttons:
            # keyboard.press(key)
            print(f"Pressed: {key}")
        else:
            print(f"Released: {key}")

    current_pressed_buttons = new_pressed_buttons
    

server_ip = ""
server_port = 12345

def handle_client(client_socket, client_address):
    print(f"Connected to {client_address}")
    last_print_time = time.time()
    print_interval = 1  # seconds

    try:
        trigger_states = {'left_mouse': False, 'right_mouse': False}
        while True:
            data = b""
            while True:
                packet = client_socket.recv(4096)
                if not packet:
                    raise Exception("Client disconnected")
                data += packet
                try:
                    end = data.index(b'\n')
                    joystick_state = json.loads(data[:end].decode())
                    data = data[end + 1:]
                    break
                except (ValueError, IndexError):
                    continue

            current_time = time.time()
            if current_time - last_print_time > print_interval:
                # print(joystick_state)
                last_print_time = current_time

            keyPress(joystick_state)
           
            

    except Exception as e:
        print(f"Error: {e}")

    print(f"Connection closed for {client_address}")
    client_socket.close()

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((server_ip, server_port))
server_socket.listen(1)
print(f"Listening for connections...")

while True:
    try:
        client_socket, client_address = server_socket.accept()
        client_handler = threading.Thread(target=handle_client, args=(client_socket, client_address))
        client_handler.start()
    except KeyboardInterrupt:
        print("Shutting down the server...")
        break

server_socket.close()
