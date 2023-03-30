import pygame
import time

pygame.init()

joystick = None
for i in range(pygame.joystick.get_count()):
    joystick = pygame.joystick.Joystick(i)
    if joystick.get_init():
        break

if not joystick:
    print("No joystick found!")
    exit(1)

joystick.init()

try:
    left_mouse_pressed = False
    right_mouse_pressed = False

    while True:
        pygame.event.pump()

        for button in range(joystick.get_numbuttons()):
            if joystick.get_button(button):
                print(f"Button {button} is pressed")

        for hat_id in range(joystick.get_numhats()):
            hat_value = joystick.get_hat(hat_id)
            if hat_value != (0, 0):
                print(f"Hat {hat_id} is pressed: {hat_value}")

        left_trigger = joystick.get_axis(4)
        right_trigger = joystick.get_axis(5)

        if left_trigger > 0.5 and not left_mouse_pressed:
            print(f"Left Trigger {left_trigger}: Pressed")
            left_mouse_pressed = True
        elif left_trigger <= 0.5 and left_mouse_pressed:
            print("Left Trigger: Released")
            left_mouse_pressed = False

        if right_trigger > 0.5 and not right_mouse_pressed:
            print(f"Right Trigger {right_trigger}: Pressed")
            right_mouse_pressed = True
        elif right_trigger <= 0.5 and right_mouse_pressed:
            print("Right Trigger: Released")
            right_mouse_pressed = False

        time.sleep(0.01)

except KeyboardInterrupt:
    print("Exiting...")

pygame.quit()
