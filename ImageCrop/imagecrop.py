import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk


# Function to initialize the window size based on 50% of screen resolution
def init_window_size(window):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    # Resize window to 50% of the screen size
    window_width = int(screen_width * 0.5)
    window_height = int(screen_height * 0.5)

    # Center the window
    x_position = int((screen_width - window_width) / 2)
    y_position = int((screen_height - window_height) / 2)

    window.geometry(f'{window_width}x{window_height}+{x_position}+{y_position}')
    return window_width, window_height


# Function to open and load the image
def load_image():
    global img, resized_img, img_label, img_canvas, tk_image, canvas_img, start_x, start_y, rect, canvas_width, canvas_height, img_x_offset, img_y_offset

    # Allow selecting any image file without filtering by extension
    file_path = filedialog.askopenfilename(
        filetypes=[("All Image Files", "*.*")]
    )

    if not file_path:
        messagebox.showwarning("Warning", "No image selected!")
        return

    try:
        img = Image.open(file_path)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to open image: {e}")
        return

    # Resize the image to fit the window
    fit_image_to_window(window_width, window_height)


def fit_image_to_window(window_width, window_height):
    global img, resized_img, img_label, img_canvas, tk_image, canvas_img, rect, canvas_width, canvas_height, img_x_offset, img_y_offset

    img_ratio = img.width / img.height
    window_ratio = window_width / window_height

    if img_ratio > window_ratio:
        new_width = window_width
        new_height = int(window_width / img_ratio)
    else:
        new_height = window_height
        new_width = int(window_height * img_ratio)

    resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
    tk_image = ImageTk.PhotoImage(resized_img)

    canvas_width = window_width
    canvas_height = window_height

    # Calculate image offsets to center it
    img_x_offset = (canvas_width - new_width) // 2
    img_y_offset = (canvas_height - new_height) // 2

    # Display image in the center of the canvas
    img_canvas.delete("all")
    img_canvas.config(width=canvas_width, height=canvas_height)
    canvas_img = img_canvas.create_image(img_x_offset, img_y_offset, anchor="nw", image=tk_image)
    rect = None


# Function to handle mouse click for cropping area
def on_mouse_down(event):
    global start_x, start_y, rect
    start_x, start_y = event.x, event.y
    if rect:
        img_canvas.delete(rect)
    rect = img_canvas.create_rectangle(start_x, start_y, start_x, start_y, outline='red', width=2)


# Function to handle mouse drag to show cropping area
def on_mouse_drag(event):
    global rect
    img_canvas.coords(rect, start_x, start_y, event.x, event.y)


# Function to crop the selected area
def crop_image():
    global img, start_x, start_y, rect, resized_img, img_x_offset, img_y_offset

    if img is None:
        messagebox.showwarning("Warning", "Please load an image first!")
        return

    if not rect:
        messagebox.showwarning("Warning", "Please select an area to crop first!")
        return

    # Get the canvas coordinates of the rectangle
    x0, y0, x1, y1 = img_canvas.coords(rect)

    # Adjust coordinates by image offsets
    x0_adj = x0 - img_x_offset
    y0_adj = y0 - img_y_offset
    x1_adj = x1 - img_x_offset
    y1_adj = y1 - img_y_offset

    # Ensure the coordinates are within image bounds
    x0_adj = max(0, x0_adj)
    y0_adj = max(0, y0_adj)
    x1_adj = min(resized_img.width, x1_adj)
    y1_adj = min(resized_img.height, y1_adj)

    # Convert canvas coordinates to original image coordinates
    scale_x = img.width / resized_img.width
    scale_y = img.height / resized_img.height

    left = int(x0_adj * scale_x)
    top = int(y0_adj * scale_y)
    right = int(x1_adj * scale_x)
    bottom = int(y1_adj * scale_y)

    cropped_img = img.crop((left, top, right, bottom))

    # Save the cropped image
    save_path = filedialog.asksaveasfilename(defaultextension=".png",
                                             filetypes=[("PNG files", "*.png"),
                                                        ("JPEG files", "*.jpg;*.jpeg"),
                                                        ("All Files", "*.*")])
    if save_path:
        cropped_img.save(save_path)
        messagebox.showinfo("Success", f"Image saved as {save_path}")


# Initialize the main window
window = tk.Tk()
window.title("Image Cropping Application")

# Set window size to 50% of screen resolution
window_width, window_height = init_window_size(window)

# Create frame for the canvas and buttons
main_frame = tk.Frame(window)
main_frame.grid(row=0, column=0, sticky="nsew")

# Configure grid layout
window.grid_rowconfigure(0, weight=1)
window.grid_columnconfigure(0, weight=1)
main_frame.grid_rowconfigure(0, weight=1)
main_frame.grid_columnconfigure(0, weight=1)

# Create canvas to display the image
img_canvas = tk.Canvas(main_frame)
img_canvas.grid(row=0, column=0, sticky="nsew")

# Add mouse event bindings for cropping
img_canvas.bind("<ButtonPress-1>", on_mouse_down)
img_canvas.bind("<B1-Motion>", on_mouse_drag)

# Create frame for buttons
button_frame = tk.Frame(main_frame)
button_frame.grid(row=1, column=0, pady=10)

load_button = tk.Button(button_frame, text="Load Image", command=load_image, width=20, height=2)
load_button.pack(side=tk.LEFT, padx=5)

crop_button = tk.Button(button_frame, text="Crop and Save Image", command=crop_image, width=20, height=2)
crop_button.pack(side=tk.LEFT, padx=5)

# Variables to store the image and drawing parameters
img = None
resized_img = None
tk_image = None
canvas_img = None
start_x = start_y = 0
rect = None
canvas_width = canvas_height = 0
img_x_offset = img_y_offset = 0

# Start the tkinter main loop
window.mainloop()
