import pygame
import time
import keyboard
import ctypes


# Initialize pygame
pygame.init()

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

# Find the first available joystick
joystick = None
for i in range(pygame.joystick.get_count()):
    joystick = pygame.joystick.Joystick(i)
    if joystick.get_init():
        break

if not joystick:
    print("No joystick found!")
    exit(1)

joystick.init()

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




try:
    trigger_states = {'left_mouse': False, 'right_mouse': False}

    left_mouse_pressed = False
    right_mouse_pressed = False

    while True:
        pygame.event.pump()

        
        # Button inputs
        current_pressed_buttons = set()
        for button, key in key_mapping.items():
            key_state = joystick.get_button(button)
            if key_state:
                current_pressed_buttons.add(button)
            else:
                if button in current_pressed_buttons:
                    current_pressed_buttons.remove(button)

        # Check for button combinations
        for button_combo, key in button_combination_mapping.items():
            if all(button in current_pressed_buttons for button in button_combo):
                print(f"Button combination {button_combo} is pressed")
                if key not in pressed_keys:
                    keyboard.press(key)
                    pressed_keys.add(key)
            elif key in pressed_keys:
                keyboard.release(key)
                pressed_keys.remove(key)

        # Press and release single button keybinds
        for button, key in key_mapping.items():
            key_state = joystick.get_button(button)
            current_key_state = key in pressed_keys

            combo_key_used = False
            for combo, combo_key in button_combination_mapping.items():
                if button in combo:
                    if all(b in current_pressed_buttons for b in combo):
                        combo_key_used = True
                        break

            if key_state and not current_key_state:
                if not combo_key_used:
                    print(key)
                    keyboard.press(key)
                    pressed_keys.add(key)
                elif combo_key_used and all(b not in current_pressed_buttons for b in combo):
                    keyboard.release(combo_key)
                    pressed_keys.remove(combo_key)

            elif not key_state and current_key_state and not combo_key_used:
                keyboard.release(key)
                pressed_keys.remove(key)





        # Left analog stick
        left_x_axis = joystick.get_axis(0)
        left_y_axis = joystick.get_axis(1)

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
        right_x_axis = joystick.get_axis(2)
        right_y_axis = joystick.get_axis(3)

        if abs(right_x_axis) > joystick_deadzone or abs(right_y_axis) > joystick_deadzone:
            dx = int(right_x_axis * mouse_sensitivity)
            dy = int(right_y_axis * mouse_sensitivity)
            mouse_action(dx, dy)
        
        # D-pad inputs
        hat_value = joystick.get_hat(0)
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
        left_trigger = joystick.get_axis(4)
        right_trigger = joystick.get_axis(5)

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



        time.sleep(0.01)

except KeyboardInterrupt:
    print("Exiting...")

# Quit pygame
pygame.quit()
