import pygame
import time

# Initialize pygame
pygame.init()

# Find the first available joystick
joystick = None
for i in range(pygame.joystick.get_count()):
    joystick = pygame.joystick.Joystick(i)
    if joystick.get_init():
        break

if not joystick:
    print("No joystick found!")
    print("test")
    exit(1)

joystick.init()

try:
    left_mouse_pressed = False
    right_mouse_pressed = False

    while True:
        pygame.event.pump()

        # Button inputs
        for button in range(joystick.get_numbuttons()):
            if joystick.get_button(button):
                print(f"Button {button} is pressed")

        # Trigger buttons
        print(joystick.get_axis(3))
        left_trigger = joystick.get_axis(4)
        right_trigger = joystick.get_axis(5)

        # Left trigger (aim)
        if left_trigger > 0.5 and not left_mouse_pressed:
            print(left_trigger)
            print("left mouse down")
            left_mouse_pressed = True
        elif left_trigger <= 0.5 and left_mouse_pressed:
            print("left mouse up")
            left_mouse_pressed = False

        # Right trigger (shoot)
        if right_trigger > 0.5 and not right_mouse_pressed:
            print(right_trigger)
            print("right mouse down")
            right_mouse_pressed = True
        elif right_trigger <= 0.5 and right_mouse_pressed:
            print("right mouse up")
            right_mouse_pressed = False

        time.sleep(0.01)

except KeyboardInterrupt:
    print("Exiting...")

# Quit pygame
pygame.quit()
