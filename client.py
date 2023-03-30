import socket
import json
import pygame

# Load config
with open("config.json", "r") as f:
    config = json.load(f)

server_ip = config["server_ip"]
server_port = config["server_port"]

pygame.init()
pygame.joystick.init()
joystick = pygame.joystick.Joystick(0)
joystick.init()

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((server_ip, server_port))

try:
    while True:
        pygame.event.pump()

        joystick_state = {
            'axes': [joystick.get_axis(i) for i in range(joystick.get_numaxes())],
            'buttons': [joystick.get_button(i) for i in range(joystick.get_numbuttons())],
            'hats': [joystick.get_hat(i) for i in range(joystick.get_numhats())],
        }

        s.sendall((json.dumps(joystick_state) + '\n').encode())

except KeyboardInterrupt:
    print("Exiting...")

s.close()
