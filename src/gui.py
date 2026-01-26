import tkinter as tk
from tkinter import messagebox
import serial
import threading
import time
from PIL import Image, ImageTk 
import random
import os
import glob

# --- Initialization & Serial (Kept your logic) ---
try:
    ser = serial.Serial('/dev/ttyACM0', 115200, timeout=1)
except Exception as e:
    ser = None
    print(f"Serial port error: {e}")

DROP_X_RANGE = (40, 250)  # Adjusted range to fit the new canvas width
BUCKET_Y_POSITION = 360   # Move bucket up
BUCKET_X_POSITION = 20    

# --- GIF Player Variables ---
gif_files = []
current_gif_index = 0
gif_frames = []
current_frame_index = 0
gif_label = None

# --- Functions ---
def send_data():
    try:
        values = [entry.get() if entry.get().isdigit() and 0 <= int(entry.get()) <= 255 else "0" for entry in entries]
        message = ", ".join(values)
        if ser: ser.write(message.encode())
        print(f"Sent: {message}")
    except Exception as e:
        print(f"Error sending data: {e}")

def read_serial():
    while True:
        if ser:
            try:
                data = ser.readline().decode().strip()
                if data.isdigit() and 1 <= int(data) <= 4:
                    result_label.config(text=f"CHEVAL {data} A GAGNÉ!")
            except Exception as e:
                print(f"Error reading data: {e}")

if ser:
    threading.Thread(target=read_serial, daemon=True).start()

def start_countdown():
    def countdown_step(count):
        if count > 0:
            countdown_label.config(text=str(count))
            root.after(1000, countdown_step, count - 1)
        else:
            countdown_label.config(text="GO!")
            root.after(1000, lambda: countdown_label.config(text=""))
            send_data()
    countdown_step(3)

def drop_image():
    try:
        # Using the smaller drop image
        start_x = random.randint(DROP_X_RANGE[0], DROP_X_RANGE[1])
        drop = canvas.create_image(start_x, 0, image=drop_photo, anchor="center")

        def animate_drop(y):
            if y < BUCKET_Y_POSITION:
                canvas.coords(drop, start_x, y)
                canvas.after(10, animate_drop, y + 5)
            else:
                canvas.delete(drop)
        animate_drop(0)
    except Exception as e:
        print(f"Animation error: {e}")

def start_dropping():
    drop_image()
    root.after(1000, start_dropping)

def load_gif_files():
    """Load all GIF file paths from include/gifs folder"""
    global gif_files
    gif_folder = "include/gifs"
    if os.path.exists(gif_folder):
        gif_files = sorted(glob.glob(os.path.join(gif_folder, "*.gif")))
        print(f"Found {len(gif_files)} GIF files: {gif_files}")
    else:
        print(f"GIF folder not found: {gif_folder}")
        gif_files = []

def load_gif_frames(gif_path):
    """Load all frames from a GIF file"""
    global gif_frames
    gif_frames = []
    try:
        gif = Image.open(gif_path)
        # Get original dimensions
        original_width, original_height = gif.size
        
        # Target size (max dimension)
        max_size = 400
        
        # Calculate new size maintaining aspect ratio
        ratio = min(max_size / original_width, max_size / original_height)
        new_width = int(original_width * ratio)
        new_height = int(original_height * ratio)
        
        while True:
            frame = gif.copy().resize((new_width, new_height), Image.Resampling.LANCZOS)
            gif_frames.append(ImageTk.PhotoImage(frame))
            gif.seek(gif.tell() + 1)
    except EOFError:
        pass  # End of GIF frames
    except Exception as e:
        print(f"Error loading GIF {gif_path}: {e}")

def animate_gif():
    """Animate the current GIF, move to next GIF when done"""
    global current_frame_index, current_gif_index
    
    if not gif_files or not gif_frames:
        return
    
    # Update the label with current frame
    gif_label.config(image=gif_frames[current_frame_index])
    current_frame_index += 1
    
    # Check if we've shown all frames of current GIF
    if current_frame_index >= len(gif_frames):
        current_frame_index = 0
        current_gif_index = (current_gif_index + 1) % len(gif_files)
        load_gif_frames(gif_files[current_gif_index])
    
    # Schedule next frame (adjust delay as needed, 100ms default)
    root.after(100, animate_gif)

def start_gif_player():
    """Initialize and start the GIF player"""
    global current_gif_index, current_frame_index
    load_gif_files()
    if gif_files:
        current_gif_index = 0
        current_frame_index = 0
        load_gif_frames(gif_files[0])
        animate_gif()

# --- GUI Setup ---
root = tk.Tk()
root.title("LA COURSE DE CHEVAUX GELGIF")
root.geometry("1000x700") # Made slightly wider to fit everything
root.configure(bg="#f0f0f0")

title = tk.Label(root, text="LA COURSE DE CHEVAUX GELGIF", bg="#f0f0f0", font=("Arial", 20, "bold"))
title.pack(pady=10)

main_frame = tk.Frame(root, bg="#f0f0f0")
main_frame.pack(fill=tk.BOTH, expand=True)

# 1. LOAD ASSETS ONCE
try:
    # Main Sidebar Image
    path = "include/onepisse.png"
    original_img = Image.open(path)
    bucket_img = ImageTk.PhotoImage(original_img.resize((250, 350), Image.Resampling.LANCZOS))
    
    # Drop Image
    drop_raw = Image.open("include/droppisse.jpeg")
    drop_photo = ImageTk.PhotoImage(drop_raw.resize((40, 40), Image.Resampling.LANCZOS))
except Exception as e:
    print(f"Asset loading error: {e}")

# 2. CANVAS (Now positioned to the left, width matches bucket)
canvas = tk.Canvas(main_frame, bg="#ffffff", width=300, height=600, highlightthickness=1)
canvas.pack(side=tk.LEFT, padx=20, fill=tk.Y)
bucket = canvas.create_image(BUCKET_X_POSITION, BUCKET_Y_POSITION, image=bucket_img, anchor="nw")

# 3. CENTER PANEL (GIF Player)
gif_frame = tk.Frame(main_frame, bg="#f0f0f0")
gif_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20)

gif_label = tk.Label(gif_frame, bg="#f0f0f0")
gif_label.pack(expand=True)

# 4. RIGHT PANEL (Inputs) - white background
input_frame = tk.Frame(main_frame, bg="#f0f0f0")
input_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=40)

entries = []
for i in range(4):
    f = tk.Frame(input_frame, bg="#f0f0f0")
    f.pack(pady=10)
    tk.Label(f, text=f"Mise {i+1}:", font=("Arial", 30), bg="#f0f0f0").pack(side=tk.LEFT)
    e = tk.Entry(f, width=10, font=("Arial", 30))
    e.pack(side=tk.LEFT, padx=10)
    entries.append(e)

send_button = tk.Button(input_frame, text="GO!", command=start_countdown, bg="#4CAF50", fg="white", font=("Arial", 50))
send_button.pack(pady=20)

result_label = tk.Label(root, text="", bg="#f0f0f0", font=("Arial", 14), fg="blue")
result_label.pack(pady=10)

# Large countdown at bottom right
countdown_label = tk.Label(root, text="", font=("Arial", 80, "bold"), fg="red", bg="#f0f0f0", justify='center')
countdown_label.place(relx=1.0, rely=1.0, anchor="se", x=-200, y=-20)

start_dropping()
start_gif_player()
root.mainloop()