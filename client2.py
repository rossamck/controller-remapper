import pygame
import time
import socket
import json
import tkinter as tk
from tkinter import messagebox

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

# Request available mappings
client_socket.sendall(b"request_mappings")

# Receive available mappings
mapping_data = client_socket.recv(4096).decode()
available_mappings = json.loads(mapping_data)

# Tkinter mapping selection
def on_mapping_selected():
    selected_mapping.set(mapping_listbox.get(mapping_listbox.curselection()))
    selection_window.quit()

selection_window = tk.Tk()
selection_window.title("Mapping Selection")

mapping_listbox = tk.Listbox(selection_window)
for mapping in available_mappings:
    mapping_listbox.insert(tk.END, mapping)
mapping_listbox.pack()

selected_mapping = tk.StringVar()

select_button = tk.Button(selection_window, text="Select Mapping", command=on_mapping_selected)
select_button.pack()

selection_window.mainloop()
selected_mapping_name = selected_mapping.get()
selection_window.destroy()

# Notify server of the chosen mapping
client_socket.sendall(("use_mapping:" + selected_mapping_name).encode())

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
