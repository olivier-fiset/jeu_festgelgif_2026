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
NOM_CHEVAL_BLEUF = "BENIMOUNE"
NOM_CHEVAL_BLEUP = "GROS ZOURS SALE BIO"
NOM_CHEVAL_NOIR = "CHEVAL NOIR"
NOM_CHEVAL_JAUNE = "CHEVAL JAUNE"    

# --- GIF Player Variables ---
gif_frames = []
gif_index = 0
current_file = None
gif_label = None
gif_frames_ref = []  # Add this to prevent garbage collection

# Add these constants near the top of your file
GIF_FOLDER = "include/gifs"  # Adjust path as needed
SUPPORTED_EXTENSIONS = ('.gif', '.png', '.jpg', '.jpeg', '.bmp')
IMAGE_DISPLAY_TIME = 3000  # 3 seconds in milliseconds

# --- Functions ---
def send_data():
    try:
        values = [entry.get() if entry.get().isdigit() and 0 <= int(entry.get()) <= 255 else "0" for entry in entries]
        message = ", ".join(values)
        if ser:
            ser.write((message + "\n").encode())
        print(f"Sent: {message}")
    except Exception as e:
        print(f"Error sending data: {e}")

def read_serial():
    while True:
        if ser:
            try:
                data = ser.readline().decode().strip()
                if data.isdigit() and 1 <= int(data) <= 4:
                    if int(data) == 1:
                        result_label.config(text=f"{NOM_CHEVAL_BLEUP} A GAGNÉ!")
                    elif int(data) == 2:
                        result_label.config(text=f"{NOM_CHEVAL_BLEUF} A GAGNÉ!")
                    elif int(data) == 3:
                        result_label.config(text=f"{NOM_CHEVAL_JAUNE} A GAGNÉ!")
                    elif int(data) == 4:
                        result_label.config(text=f"{NOM_CHEVAL_NOIR} A GAGNÉ!")
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

def get_random_media_file():
    """Get a random file from the gif folder."""
    if not os.path.exists(GIF_FOLDER):
        print(f"ERROR: Folder '{GIF_FOLDER}' does not exist!")
        return None
    files = [f for f in os.listdir(GIF_FOLDER) 
             if f.lower().endswith(SUPPORTED_EXTENSIONS)]
    if not files:
        print(f"ERROR: No supported files found in '{GIF_FOLDER}'")
        return None
    chosen = os.path.join(GIF_FOLDER, random.choice(files))
    print(f"Selected media file: {chosen}")
    return chosen

def load_media_file(filepath):
    """Load a GIF or image file and return frames list."""
    global gif_frames, gif_index, gif_frames_ref
    gif_frames = []
    gif_frames_ref = []  # Clear old references
    gif_index = 0
    
    if not filepath or not os.path.exists(filepath):
        return False
    
    try:
        img = Image.open(filepath)
        
        if filepath.lower().endswith('.gif') and hasattr(img, 'n_frames') and img.n_frames > 1:
            # It's an animated GIF
            for frame_num in range(img.n_frames):
                img.seek(frame_num)
                frame = img.copy().convert('RGBA')
                frame = frame.resize((300, 300), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(frame)
                gif_frames.append(photo)
                gif_frames_ref.append(photo)  # Keep reference
            return True
        else:
            # It's a static image
            img = img.convert('RGBA')
            img = img.resize((300, 300), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            gif_frames.append(photo)
            gif_frames_ref.append(photo)  # Keep reference
            return True
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
        return False

def start_gif_player():
    """Start playing random media from the gif folder."""
    load_next_media()

def load_next_media():
    """Load the next random media file."""
    global current_file
    current_file = get_random_media_file()
    if current_file and load_media_file(current_file):
        print(f"Loaded {len(gif_frames)} frames from {current_file}")
        play_gif_frame()
    else:
        # Show placeholder text when no media is available
        gif_label.configure(image='', text="No media found\nin 'gif' folder", 
                          font=("Arial", 14), fg="gray")
        # Retry after 5 seconds
        root.after(5000, load_next_media)

def play_gif_frame():
    """Play GIF frames or display static image."""
    global gif_index
    
    if not gif_frames:
        root.after(1000, load_next_media)
        return
    
    # Update the label with current frame
    gif_label.configure(image=gif_frames[gif_index])
    
    if len(gif_frames) == 1:
        # Static image - display for 3 seconds then load next
        root.after(IMAGE_DISPLAY_TIME, load_next_media)
    else:
        # Animated GIF - advance to next frame
        gif_index += 1
        if gif_index >= len(gif_frames):
            # GIF finished, load next media
            gif_index = 0
            root.after(100, load_next_media)
        else:
            # Continue GIF animation (adjust delay as needed)
            root.after(100, play_gif_frame)

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

noms = [NOM_CHEVAL_BLEUP, NOM_CHEVAL_BLEUF, NOM_CHEVAL_JAUNE, NOM_CHEVAL_NOIR]
entries = []
for i in range(4):
    f = tk.Frame(input_frame, bg="#f0f0f0")
    f.pack(pady=10)
    tk.Label(f, text=f"Mise {noms[i]}:", font=("Arial", 10), bg="#f0f0f0").pack(side=tk.LEFT)
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