import pygame
import time
import socket
import json

# Load config
with open("config.json") as config_file:
    config = json.load(config_file)

# Initialize pygame
pygame.init()

# Set joystick deadzone
joystick_deadzone = 0.2
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

# Connect to the server
server_address = (config["server_ip"], config["server_port"])
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(server_address)

try:
    while True:
        pygame.event.pump()

        # Collect controller data
        button_data = [joystick.get_button(i) for i in range(joystick.get_numbuttons())]
        axis_data = [joystick.get_axis(i) for i in range(joystick.get_numaxes())]
        hat_data = [joystick.get_hat(i) for i in range(joystick.get_numhats())]

        # Send data to server
        controller_data = {"buttons": button_data, "axes": axis_data, "hats": hat_data}
        data_to_send = json.dumps(controller_data).encode() + b'\n'
        client_socket.sendall(data_to_send)

        time.sleep(0.01)

except KeyboardInterrupt:
    print("Exiting...")

# Close the socket
client_socket.close()

# Quit pygame
pygame.quit()
