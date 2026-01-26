import tkinter as tk
from tkinter import messagebox
import serial
import threading
import time

# Initialize serial communication
try:
    ser = serial.Serial('/dev/ttyACM0', 115200, timeout=1)
except Exception as e:
    ser = None
    print(f"Serial port error: {e}")

# Function to send data over serial
def send_data():
    try:
        values = []
        for entry in entries:
            value = entry.get()
            if not value.isdigit() or not (0 <= int(value) <= 255):
                value = "0"
            values.append(value)
        message = ", ".join(values)
        if ser:
            ser.write(message.encode())
        print(f"Sent: {message}")
    except Exception as e:
        print(f"Error sending data: {e}")

# Function to read data from serial
def read_serial():
    while True:
        if ser:
            try:
                data = ser.readline().decode().strip()
                if data.isdigit() and 1 <= int(data) <= 4:
                    result_label.config(text=f"CHEVAL {data} A GAGNÉ!")
            except Exception as e:
                print(f"Error reading data: {e}")

# Start a thread to read serial data
if ser:
    threading.Thread(target=read_serial, daemon=True).start()

# Function to handle the countdown and send data
def start_countdown():
    countdown_label.config(text="3")
    root.update()
    time.sleep(1)
    countdown_label.config(text="2")
    root.update()
    time.sleep(1)
    countdown_label.config(text="1")
    root.update()
    time.sleep(1)
    countdown_label.config(text="GO!")
    root.update()
    time.sleep(1)
    countdown_label.config(text="")  # Clear the countdown
    send_data()  # Call the send_data function after the countdown

# Create the GUI
root = tk.Tk()
root.title("LA COURSE DE CHEVAUX GELGIF")
root.geometry("800x600")
root.configure(bg="#f0f0f0")

# Create a title at the top center
title = tk.Label(root, text="LA COURSE DE CHEVAUX GELGIF", bg="#f0f0f0", font=("Arial", 20, "bold"))
title.pack(pady=10)

# Create a frame for the layout
main_frame = tk.Frame(root, bg="#f0f0f0")
main_frame.pack(fill=tk.BOTH, expand=True)

# Add a space for the image on the left
image_frame = tk.Frame(main_frame, bg="#f0f0f0", width=200)
image_frame.pack(side=tk.LEFT, fill=tk.Y)

# Add a placeholder for the image
image_placeholder = tk.Label(image_frame, text="Image Here", bg="#d9d9d9", width=20, height=12)  # Increased size
image_placeholder.pack(pady=20)  # Added more padding

# Create a frame for the text boxes and button on the right
input_frame = tk.Frame(main_frame, bg="#f0f0f0")
input_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=40, pady=20)  # Added more padding to center vertically

# Create text boxes with larger fonts and sizes
entries = []
for i in range(4):
    frame = tk.Frame(input_frame, bg="#f0f0f0")
    frame.pack(pady=15, anchor="center")  # Increased spacing and centered rows
    label = tk.Label(frame, text=f"Mise {i+1}:", bg="#f0f0f0", font=("Arial", 18))  # Increased font size
    label.pack(side=tk.LEFT, padx=15)
    entry = tk.Entry(frame, width=20, font=("Arial", 18))  # Increased font size and width
    entry.pack(side=tk.LEFT, padx=15)
    entries.append(entry)

# Create the countdown label
countdown_label = tk.Label(input_frame, text="", bg="#f0f0f0", font=("Arial", 24, "bold"), fg="red")
countdown_label.pack(pady=20)

# Create the send button with larger font and centered alignment
send_button = tk.Button(input_frame, text="ENVOYER", command=start_countdown, bg="#4CAF50", fg="white", font=("Arial", 20))  # Increased font size
send_button.pack(pady=40)  # Added more spacing below the button

# Create the result label
result_label = tk.Label(root, text="", bg="#f0f0f0", font=("Arial", 14), fg="blue")
result_label.pack(pady=10)

# Run the GUI
root.mainloop()