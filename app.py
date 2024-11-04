import os
import customtkinter as ctk
from tkinter import filedialog, messagebox, Toplevel, Label, PhotoImage
from PIL import Image, ImageTk, ImageOps
from pathlib import Path 
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv
import winsound
import shutil
import threading
import pyrebase
import logging
import queue


# Configure logging
logging.basicConfig(level=logging.DEBUG, filename='app_debug.log', filemode='a',
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize the customtkinter appearance
ctk.set_appearance_mode("dark")  # Modes: "System" (default), "Dark", "Light"
ctk.set_default_color_theme("dark-blue")  # Themes: "blue" (default), "green", "dark-blue")

# Create the main window
app = ctk.CTk()
app.title("Machine Staging")
app.geometry("620x800")
app.maxsize(620, app.winfo_screenheight())
app.grid_rowconfigure(0, minsize=100, weight=1)  # Set minimum size for row 0, where frame1 is located
app.grid_columnconfigure(0, weight=0)  # Ensure column is also configured
# Configure the bottom padding row
app.grid_rowconfigure(1, minsize=1)  # 20 pixels of padding

# Add an empty frame or label in row 1
bottom_padding = ctk.CTkFrame(app, width=600, height=1)  # Set width and height for padding frame
bottom_padding.grid(row=1, column=0, pady=(50,0))
# Function to switch frames
def switch_frame(frame):
    frame.tkraise()

# Load environment variables from .env file
load_dotenv()

# Firebase configuration
fireConfig = {
    "apiKey": os.getenv("API_KEY"),
    "authDomain": os.getenv("AUTH_DOMAIN"),
    "databaseURL": os.getenv("DATABASE_URL"),
    "storageBucket": os.getenv("STORAGE_BUCKET"),
}

# Initialize Firebase
firebase = pyrebase.initialize_app(fireConfig)
db = firebase.database()

# Function to initialize machine_states in Firebase as a dictionary
def initialize_machine_states_in_firebase():
    existing_data = db.child('machine_states').get().val()
    if existing_data is None or isinstance(existing_data, list):
        # Initialize machine_states as a dictionary
        total_machines = 30  # Adjust this number as needed
        initial_states = {str(i): 0 for i in range(1, total_machines + 1)}
        db.child('machine_states').set(initial_states)

# Call the initialization function
initialize_machine_states_in_firebase()

# Frame 1 - Machine Selection
frame1 = ctk.CTkFrame(app, width=500, height=700)
frame1.grid(row=0, column=0, sticky="nsew", padx=(20, 0), pady=(10, 10))

# Frame 2 - File Uploads (One Column Layout)
frame2 = ctk.CTkFrame(app, width=500, height=700)
frame2.grid(row=0, column=0, sticky="nsew", padx=(20, 0), pady=(10, 10))

# Frame 3 - Scrollable Frame for File Assignment Display
frame3 = ctk.CTkFrame(app, width=500, height=700)
frame3.grid(row=0, column=0, sticky="nsew", padx=(20, 0), pady=(10, 10))

# ---- Frame 1: Machine Selection with Firebase Integration ----

# Create "IN - USE" and "AVAILABLE" checkboxes for display above the "Select All Machines" button
in_use_checkbox = ctk.CTkCheckBox(
    frame1,
    text="IN - USE",
    state="disabled",  # Make it non-clickable
    variable=ctk.IntVar(value=0)  # Unchecked state
)
in_use_checkbox.grid(row=5, column=1, sticky="e", pady=5)

available_checkbox = ctk.CTkCheckBox(
    frame1,
    text="AVAILABLE",
    state="disabled",  # Make it non-clickable
    variable=ctk.IntVar(value=1)  # Checked state
)
available_checkbox.grid(row=5, column=2, sticky="w", pady=5)

# Function to toggle check/uncheck all machines
def toggle_all_machines():
    # Check if all machines are selected
    all_selected = all(machine_states[machine_num].get() == 1 for machine_num in range(1, 12))
    
    # Toggle based on current state
    new_state = 0 if all_selected else 1  # Set to 0 if all selected, otherwise set to 1
    for machine_num in range(1, 12):
        machine_states[machine_num].set(new_state)  # Set each machine to new state
        update_image_funcs[machine_num]()           # Update the image

    # Update button text to indicate the opposite action for the next click
    toggle_all_button.configure(text="Uncheck All" if new_state == 1 else "Check All")

# Create the "Check/Uncheck All Machines" toggle button
toggle_all_button = ctk.CTkButton(
    frame1, text="Check All", command=toggle_all_machines
)
toggle_all_button.grid(row=6, column=1, columnspan=2, pady=1)

# Label for the page
label1 = ctk.CTkLabel(frame1, text="Select Machines to Stage", font=("Arial", 20))
label1.grid(row=7, column=1, columnspan=2, pady=2)

machine_images = {}
desired_width = 50
desired_height = 50

for i in range(1, 31):
    unselected_image_path = f"images/unselected/image-m-{i}.png"
    selected_image_path = f"images/selected/image-m-{i}-selected.png"

    # Load and resize unselected image
    try:
        normal_image = Image.open(unselected_image_path).resize((desired_width, desired_height))
        normal_ctk_image = ctk.CTkImage(light_image=normal_image, dark_image=normal_image,
                                        size=(desired_width, desired_height))
    except Exception as e:
        print(f"Error loading unselected image for machine {i}: {e}")
        continue  # Skip to the next iteration

    # Load and resize selected image
    try:
        selected_image = Image.open(selected_image_path).resize((desired_width, desired_height))
        selected_ctk_image = ctk.CTkImage(light_image=selected_image, dark_image=selected_image,
                                          size=(desired_width, desired_height))
    except Exception as e:
        print(f"Error loading selected image for machine {i}: {e}")
        continue  # Skip to the next iteration

    # For disabled machines, create a grayed-out image
    if i >= 12:
        # Convert to grayscale to indicate disabled
        disabled_image = ImageOps.grayscale(normal_image)
        disabled_ctk_image = ctk.CTkImage(light_image=disabled_image, dark_image=disabled_image,
                                          size=(desired_width, desired_height))
        machine_images[i] = {'normal': disabled_ctk_image, 'selected': disabled_ctk_image}
    else:
        # Store images in dictionary
        machine_images[i] = {'normal': normal_ctk_image, 'selected': selected_ctk_image}

# Layout as per your specified format
layout = [
    [(9, 0), (22, 3)],
    [(8, 0), (23, 3)],
    [(7, 0), (10, 1), (21, 2), (24, 3)],
    [(6, 0), (11, 1), (20, 2), (25, 3)],
    [(5, 0), (12, 1), (19, 2), (26, 3)],
    [(4, 0), (13, 1), (18, 2), (27, 3)],
    [(3, 0), (14, 1), (17, 2), (28, 3)],
    [(2, 0), (15, 1), (16, 2), (29, 3)],
    [(1, 0), (30, 3)],
]

# Variables to hold the state of the checkboxes (selected/unselected)
machine_states = {}          # Dictionary to store IntVars
machine_states_traces = {}   # Dictionary to store trace IDs
machine_labels = {}          # Dictionary to store image labels
update_image_funcs = {}      # Dictionary to store update functions

# Function to handle state changes and update Firebase
def on_machine_state_change(machine_num, *args):
    state = machine_states[machine_num].get()
    db.child('machine_states').child(machine_num).set(state)

# Function to update local machine state from Firebase
def update_local_machine_state(machine_num, state):
    def update_state():
        # Temporarily remove the trace to prevent recursion
        machine_states[machine_num].trace_vdelete('w', machine_states_traces[machine_num])
        # Update the IntVar
        machine_states[machine_num].set(state)
        # Update the image
        update_image_funcs[machine_num]()
        # Re-establish the trace
        trace_id = machine_states[machine_num].trace('w', lambda *args, mn=machine_num: on_machine_state_change(mn, *args))
        machine_states_traces[machine_num] = trace_id
    # Schedule the update in the main thread
    app.after(0, update_state)

# Stream handler function for Firebase
# Stream handler function
def stream_handler(message):
    if message["data"] is None:
        return

    path = message["path"]
    data = message["data"]

    # Debugging output to inspect data
    print(f"Received data at path '{path}': {data}")
    print(f"Type of data: {type(data)}")

    if path == "/":
        # Initial data or full update
        if isinstance(data, dict):
            # Data is a dictionary as expected
            for machine_num_str, state in data.items():
                machine_num = int(machine_num_str)
                update_local_machine_state(machine_num, state)
        elif isinstance(data, list):
            # Data is a list, adjust handling accordingly
            for index, state in enumerate(data):
                if state is not None:
                    machine_num = index  # Assuming machine numbers start at index 0
                    update_local_machine_state(machine_num, state)
        else:
            print("Unexpected data type received from Firebase.")
    else:
        # Data changed at a specific path
        machine_num_str = path.strip('/')
        if machine_num_str.isdigit():
            machine_num = int(machine_num_str)
            state = data
            update_local_machine_state(machine_num, state)
        else:
            print(f"Unexpected path format: {path}")

# Start the Firebase stream in a separate thread
def start_firebase_stream():
    db.child('machine_states').stream(stream_handler)

stream_thread = threading.Thread(target=start_firebase_stream)
stream_thread.daemon = True
stream_thread.start()

# Function to update images when checkbox state changes
def make_update_image(machine_num):
    def update_image():
        if machine_states[machine_num].get() == 1:
            # Selected
            image = machine_images[machine_num]['selected']
            machine_labels[machine_num].configure(text=machine_num, font=("Arial", 20))
        else:
            # Not selected
            image = machine_images[machine_num]['normal']
            machine_labels[machine_num].configure(text="")

        machine_labels[machine_num].configure(image=image)
        machine_labels[machine_num].image = image  # Keep a reference to prevent garbage collection
    return update_image

# Function to handle image click events
def on_image_click(event, machine_num):
    # Only toggle if the machine is not disabled
    if machine_num < 12:
        # Toggle the variable
        current_value = machine_states[machine_num].get()
        machine_states[machine_num].set(0 if current_value else 1)
        # Update the image
        update_image_funcs[machine_num]()

# Create the machine interface with images, checkboxes, and labels
for row_index, row in enumerate(layout, start=3):  # Start from row 3 to accommodate the buttons
    for machine_info in row:
        machine_num, col_index = machine_info
        # Create the variable for the checkbox
        var = ctk.IntVar(value=0)  # 0 for unchecked, 1 for checked
        machine_states[machine_num] = var

        # Set up a trace on the variable
        trace_id = var.trace('w', lambda *args, mn=machine_num: on_machine_state_change(mn, *args))
        machine_states_traces[machine_num] = trace_id

        # Create the image label
        image_label = ctk.CTkLabel(frame1, image=machine_images[machine_num]['normal'], text="")
        image_label.grid(row=row_index*2-1, column=col_index, padx=20, pady=5)
        machine_labels[machine_num] = image_label  # Store the label
        image_label.image = machine_images[machine_num]['normal']  # Keep a reference to prevent garbage collection

        # Define the command function for the checkbox
        update_image_func = make_update_image(machine_num)
        update_image_funcs[machine_num] = update_image_func  # Store the update function

        # Create the checkbox under the image
        checkbox = ctk.CTkCheckBox(frame1, text=f"Machine {machine_num}", variable=var, command=update_image_func)
        checkbox.grid(row=row_index*2, column=col_index, padx=20, pady=5, sticky="n")

        if machine_num >= 12:
            # Disable the checkbox
            checkbox.configure(state="disabled")
            # Disable image click
            image_label.configure(cursor="")
        else:
            # Bind click event to image label
            image_label.bind("<Button-1>", lambda event, mn=machine_num: on_image_click(event, mn))
            # Change cursor to indicate clickable image
            image_label.configure(cursor="hand2")

# Validation and switching function for submit button
def validate_and_proceed_to_frame2():
    selected_machines = [machine_num for machine_num, var in machine_states.items() if var.get() == 1]
    if not selected_machines:
        messagebox.showerror("Error", "Please select at least one machine before proceeding.")
    else:
        switch_frame(frame2)

# Submit button with validation
next_button = ctk.CTkButton(frame1, text="Submit", command=validate_and_proceed_to_frame2)
next_button.grid(row=(len(layout) * 2 + 3), column=1, columnspan=2, pady=10, sticky="we")

# ---- Frame 2: File Uploads (Scrollable Frame with Colored Buttons) ----

# Configure frame2 to expand and fill available space
frame2.grid_rowconfigure(0, weight=1)
frame2.grid_columnconfigure(0, weight=1)

# Create a scrollable frame inside frame2
scrollable_frame2 = ctk.CTkScrollableFrame(frame2)
scrollable_frame2.grid(row=0, column=0, sticky="nsew")

# Configure scrollable_frame2 to expand and fill available space
scrollable_frame2.grid_rowconfigure(0, weight=1)
scrollable_frame2.grid_columnconfigure(0, weight=1)

# Variables to store selected file paths
envelope_files = []
letter_files = []

# Function to upload envelope files
def upload_envelope_files():
    global envelope_files, letter_files
    envelope_files = list(filedialog.askopenfilenames(title="Select Envelope Files"))
    if envelope_files:
        # Update the label with the selected file names
        envelope_label.configure(
            text="\n".join([os.path.basename(f) for f in envelope_files])
        )
        # Disable the letter files upload option
        upload_letter_button.configure(state="disabled")
        letter_label.configure(text="Cannot upload letter files when envelope files are selected.")
    else:
        envelope_label.configure(text="No files selected")
        # Enable the letter files upload option if no envelope files are selected
        upload_letter_button.configure(state="normal")
        letter_label.configure(text="No files selected")

# Function to clear envelope files
def clear_envelope_files():
    global envelope_files
    envelope_files = []
    envelope_label.configure(text="No files selected")
    # Enable the letter files upload option
    upload_letter_button.configure(state="normal")
    letter_label.configure(text="No files selected")

# Function to upload letter files
def upload_letter_files():
    global letter_files, envelope_files
    letter_files = list(filedialog.askopenfilenames(title="Select Letter Files"))
    if letter_files:
        # Update the label with the selected file names
        letter_label.configure(
            text="\n".join([os.path.basename(f) for f in letter_files])
        )
        # Disable the envelope files upload option
        upload_envelope_button.configure(state="disabled")
        envelope_label.configure(text="Cannot upload envelope files when letter files are selected.")
    else:
        letter_label.configure(text="No files selected")
        # Enable the envelope files upload option if no letter files are selected
        upload_envelope_button.configure(state="normal")
        envelope_label.configure(text="No files selected")

# Function to clear letter files
def clear_letter_files():
    global letter_files
    letter_files = []
    letter_label.configure(text="No files selected")
    # Enable the envelope files upload option
    upload_envelope_button.configure(state="normal")
    envelope_label.configure(text="No files selected")

# Function to validate input and proceed
def validate_and_proceed():
    selected_machines = [machine_num for machine_num, var in machine_states.items() if var.get() == 1]
    if not envelope_files and not letter_files:
        messagebox.showerror("Error", "Please upload either envelope files or letter files before proceeding.")
    elif not selected_machines:
        messagebox.showerror("Error", "Please select at least one machine before proceeding.")
    else:
        display_file_assignments()
        switch_frame(frame3)
    transfer_button.configure(state="disabled")

# Place widgets inside the scrollable frame

# Upload Envelope Files Button
upload_envelope_button = ctk.CTkButton(
    scrollable_frame2, text="Select Envelope Files", command=upload_envelope_files
)
upload_envelope_button.grid(row=0, column=0, padx=20, pady=20, sticky="ew", columnspan=2)

# Envelope Files Label Title
envelope_label_title = ctk.CTkLabel(
    scrollable_frame2, text="Selected Envelope Files", font=("Arial", 14)
)
envelope_label_title.grid(row=1, column=0, padx=20, pady=5, sticky="ew", columnspan=2)

# Envelope Files Label
envelope_label = ctk.CTkLabel(
    scrollable_frame2, text="No files selected", font=("Arial", 12), justify="left", wraplength=500
)
envelope_label.grid(row=2, column=0, padx=20, pady=5, sticky="ew", columnspan=2)

# Clear Envelope Files Button (Red)
clear_envelope_button = ctk.CTkButton(
    scrollable_frame2,
    text="Clear Envelope Files",
    command=clear_envelope_files,
    fg_color="#CC0000",      # Dark red
    hover_color="#990000",   # Darker red on hover
    text_color="white"
)
clear_envelope_button.grid(row=3, column=0, padx=20, pady=10, sticky="ew", columnspan=2)

# Upload Letter Files Button
upload_letter_button = ctk.CTkButton(
    scrollable_frame2, text="Select Letter Files", command=upload_letter_files
)
upload_letter_button.grid(row=4, column=0, padx=20, pady=20, sticky="ew", columnspan=2)

# Letter Files Label Title
letter_label_title = ctk.CTkLabel(
    scrollable_frame2, text="Selected Letter Files", font=("Arial", 14)
)
letter_label_title.grid(row=5, column=0, padx=20, pady=5, sticky="ew", columnspan=2)

# Letter Files Label
letter_label = ctk.CTkLabel(
    scrollable_frame2, text="No files selected", font=("Arial", 12), justify="left", wraplength=500
)
letter_label.grid(row=6, column=0, padx=20, pady=5, sticky="ew", columnspan=2)

# Clear Letter Files Button (Red)
clear_letter_button = ctk.CTkButton(
    scrollable_frame2,
    text="Clear Letter Files",
    command=clear_letter_files,
    fg_color="#CC0000",      # Dark red
    hover_color="#990000",   # Darker red on hover
    text_color="white"
)
clear_letter_button.grid(row=7, column=0, padx=20, pady=20, sticky="ew", columnspan=2)

# Submit Button (Green)
submit_button_frame2 = ctk.CTkButton(
    scrollable_frame2,
    text="Submit",
    command=validate_and_proceed,
    fg_color="#008000",      # Dark green
    hover_color="#006400",   # Darker green on hover
    text_color="white"
)
submit_button_frame2.grid(row=8, column=0, padx=20, pady=20, sticky="ew", columnspan=2)

# Back Button to return to Frame 1
back_button = ctk.CTkButton(
    scrollable_frame2, text="Back", command=lambda: switch_frame(frame1)
)
back_button.grid(row=9, column=0, padx=20, pady=20, sticky="ew", columnspan=2)

# ---- Frame 3: Scrollable File Assignment Display ----

fileErrors = {}  # Dictionary to store machine_num as keys and failed file names as values
green_popup = None  # Global variable to store the green popup window reference

# Configure frame3 to expand and hold the scrollable frame and buttons
frame3.grid_rowconfigure(0, minsize=700, weight=1)
frame3.grid_rowconfigure(1, weight=0)
frame3.grid_columnconfigure(0, weight=1)
frame3.grid_columnconfigure(1, weight=1)

# Place the scrollable frame in frame3
scrollable_frame = ctk.CTkScrollableFrame(frame3)
scrollable_frame.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")

# Global variable to store file assignments
file_assignments = []  # List of tuples: (machine number, file path)

def display_file_assignments(completed=False):
    global file_assignments
    file_assignments = []  # Clear previous assignments

    for widget in scrollable_frame.winfo_children():  # Clear previous widgets
        widget.destroy()

    # Configure columns in scrollable_frame
    for i in range(4):  # Assuming 4 columns as in layout
        scrollable_frame.grid_columnconfigure(i, weight=1)

    # Add title label at the top
    title_label = ctk.CTkLabel(
        scrollable_frame,
        text="File Assignments to Machines",
        font=("Arial", 16, "bold")
    )
    title_label.grid(row=0, column=0, columnspan=4, pady=10)

    # Get all machine numbers from the layout
    all_machine_numbers = set()
    for row in layout:
        for machine_info in row:
            machine_num, col_index = machine_info
            all_machine_numbers.add(machine_num)

    # Initialize machine_assignments dict with machine numbers directly mapped to their file paths
    machine_assignments = {machine_num: None for machine_num in all_machine_numbers}

    # Determine which files are uploaded
    if envelope_files:
        all_files = envelope_files
    elif letter_files:
        all_files = letter_files
    else:
        all_files = []

    # Get selected machines and assign files in order
    selected_machines = sorted([machine_num for machine_num, var in machine_states.items() if var.get() == 1])

    # Create direct machine-to-file assignments
    for index, machine_num in enumerate(selected_machines):
        if index < len(all_files):
            file_path = all_files[index]
            file_name = os.path.basename(file_path)
            # Store the assignment
            file_assignments.append((machine_num, file_path))
            machine_assignments[machine_num] = file_name
        else:
            file_assignments.append((machine_num, None))
            machine_assignments[machine_num] = "No file assigned"

    # Now create labels in the grid layout with conditional background colors
    row_index_start = 1  # Start from row 1 since title is at row 0
    for row_index, row in enumerate(layout, start=row_index_start):
        for machine_info in row:
            machine_num, col_index = machine_info
            # Get the file assigned to this machine
            file_name = machine_assignments.get(machine_num)
            has_file = file_name is not None and file_name != "No file assigned"
            is_selected = machine_num in selected_machines
            
            # Determine label text and background color based on fileErrors and completion
            if machine_num in fileErrors:
                # Failed transfer
                label_text = f"Machine {machine_num}\nFAILED - {fileErrors[machine_num]}"
                background_color = "#FF0000"  # Red for error
            elif is_selected and has_file:
                # Successful transfer
                label_text = f"Machine {machine_num}\n{file_name}"
                background_color = "#00FF00" if completed else "#F0F0F0"  # Green if completed
            else:
                # Not selected or no file
                if file_name != "No file assigned":
                    label_text = f"Machine {machine_num} \n Machine in use or \n not selected"
                else:
                    label_text = f"Machine {machine_num} \n {file_name}"                 
                background_color = "#F0F0F0"  # Light gray for unselected

            label = ctk.CTkLabel(
                scrollable_frame,
                text=label_text,
                font=("Arial", 10),
                text_color="black",
                wraplength=100,
                width=120,
                height=60,
                corner_radius=8,
                fg_color=background_color,  # Dynamic background color based on transfer status
                justify="center"
            )
            label.grid(row=row_index, column=col_index, padx=5, pady=5)

# Define destination directories
destination_directories = [
    Path(r"\\192.168.68.81\DavWWWRoot"),
    Path(r"\\192.168.68.75\DavWWWRoot"),
    Path(r"\\192.168.68.76\DavWWWRoot"),
    Path(r"\\192.168.68.77\DavWWWRoot"),
    Path(r"\\192.168.68.78\DavWWWRoot"),
    Path(r"\\192.168.68.79\DavWWWRoot"),
    Path(r"\\192.168.68.80\DavWWWRoot"),
    Path(r"\\192.168.68.70\DavWWWRoot"),
    Path(r"\\192.168.68.82\DavWWWRoot"),
    Path(r"\\192.168.68.83\DavWWWRoot"),
    Path(r"\\192.168.68.84\DavWWWRoot")
]

# Modify the delete function to enable Transfer button after deleting .bin files
def delete_bin_files():
    # This simulates deletion of .bin files
    bin_files_deleted = 1  # Change this to 0 if you want to simulate "no files found"
    if bin_files_deleted > 0:
        messagebox.showinfo("Success", f"Deleted {bin_files_deleted} .bin files.")
    else:
        messagebox.showinfo("Info", "No .bin files found.")

def transfer_files_to_machines():
    """
    Transfers files to the specified destination directories based on file assignments
    already displayed on Frame 3. Limits transfers to the number of files available.
    """
    logging.info("Starting file transfer process.")
    
    # Filter `file_assignments` to only include entries with a valid file path
    file_assignments_with_files = [(machine_num, file_path) for machine_num, file_path in file_assignments if file_path]
    
    if not file_assignments_with_files:
        logging.warning("No file assignments with valid files found. Aborting transfer.")
        messagebox.showwarning("Warning", "No valid file assignments found.")
        return

    # Clear previous widgets in the scrollable frame and set up progress bars for each valid assignment
    for widget in scrollable_frame.winfo_children():
        widget.destroy()

    progress_bars = []
    progress_bar_mapping = {}  # Mapping of machine_num to progress bar index

    for i, (machine_num, file_path) in enumerate(file_assignments_with_files):
        label = ctk.CTkLabel(scrollable_frame, text=f"Machine {machine_num} File Transfer Progress:")
        label.pack(anchor="w", padx=10)
        progress_bar = ctk.CTkProgressBar(scrollable_frame, orientation="horizontal", width=500)
        progress_bar.pack(pady=5)
        progress_bar.set(0)
        progress_bars.append(progress_bar)
        progress_bar_mapping[machine_num] = i  # Map machine_num to the progress bar's index

    # Show "red-image.png" popup with specific dimensions as a warning until all transfers complete
    popup_red = show_popup("red-image.png", 793, 655)

    # Start concurrent file transfers
    copy_complete_event = threading.Event()
    progress_queue = queue.Queue()
    threading.Thread(
        target=start_copying_files,
        args=(file_assignments_with_files, progress_queue, copy_complete_event, progress_bar_mapping)
    ).start()
    update_progress(progress_queue, progress_bars, popup_red, copy_complete_event, progress_bar_mapping)

def start_copying_files(file_assignments, progress_queue, copy_complete_event, progress_bars):
    """
    Start file copy operations concurrently, using the filtered file_assignments list.
    Limits the operation to the number of files available.
    """
    with ThreadPoolExecutor() as executor:
        futures = []
        for machine_num, file_path in file_assignments:
            if file_path is not None and machine_num <= len(destination_directories):
                dest_dir = destination_directories[machine_num - 1]
                futures.append(executor.submit(copy_file, file_path, dest_dir, machine_num, progress_queue))
            else:
                logging.warning(f"No destination path or file for Machine {machine_num}. Skipping.")
                progress_queue.put((machine_num, -1))  # Mark progress as complete for skipped files

        for future in futures:
            future.result()  # Wait for all threads to complete

    copy_complete_event.set()  # Signal that all copies are complete

def copy_file(src_path, dest_dir, machine_num, progress_queue):
    """
    Copies the selected file to the specified destination directory and sends progress updates.
    If a file transfer fails, sends a progress of -1 to indicate failure.
    """
    dest_path = dest_dir / Path(src_path).name
    file_name = os.path.basename(src_path)  # Get the base file name
    try:
        total_size = os.path.getsize(src_path)
        copied_size = 0

        with open(src_path, "rb") as src, open(dest_path, "wb") as dest:
            while chunk := src.read(1024 * 1024):  # Read in chunks
                dest.write(chunk)
                copied_size += len(chunk)
                
                # Calculate progress as a fraction
                progress = min(1.0, copied_size / total_size)
                progress_queue.put((machine_num, progress))  # Send progress update

    except Exception as e:
        logging.error(f"Error copying file to {dest_dir} for Machine {machine_num}: {e}")
        # Confirm that we’re sending -1 to indicate failure
        logging.debug(f"Queueing failure for Machine {machine_num}")
        progress_queue.put((machine_num, -1))  # Send -1 to indicate a failure
        fileErrors[machine_num] = file_name  # Add to global fileErrors with machine_num as key and file name as value
        messagebox.showerror("Error", f"Error copying file to {dest_dir}:\n{e}")

def update_progress(progress_queue, progress_bars, popup_red, copy_complete_event, progress_bar_mapping):
    """
    Update progress bars from the queue and handle completion. Marks failed transfers in red.
    """
    failed_machines = set()  # To keep track of failed transfers by machine number

    def process_queue():
        while not progress_queue.empty():
            machine_num, progress = progress_queue.get_nowait()
            logging.debug(f"Processing queue item for Machine {machine_num} with progress: {progress}")

            # Use the mapping to get the correct progress bar index
            if machine_num in progress_bar_mapping:
                bar_index = progress_bar_mapping[machine_num]
                if progress == -1:
                    # Mark this machine as failed
                    failed_machines.add(machine_num)
                    progress_bars[bar_index].configure(fg_color="red")
                    logging.debug(f"Machine {machine_num} added to failed_machines due to transfer failure.")
                else:
                    progress_bars[bar_index].set(progress)
                    # Only set to green if the transfer is successful (progress reaches 1.0)
                    if progress >= 1.0:
                        progress_bars[bar_index].configure(fg_color="green")
            else:
                logging.warning(f"Machine {machine_num} not found in progress bar mapping.")

    process_queue()
    if not copy_complete_event.is_set():
        app.after(100, lambda: update_progress(progress_queue, progress_bars, popup_red, copy_complete_event, progress_bar_mapping))
    else:
        hide_popup(popup_red)
        show_popup("green-image.png", 749, 629, is_green=True)
        winsound.PlaySound("tada-alldone.wav", winsound.SND_FILENAME | winsound.SND_ASYNC)
        
        # Call display_file_assignments to reflect completion
        display_file_assignments(completed=True)

# Helper functions for popups
def show_popup(image_file, width, height, is_green=False):
    global green_popup
    popup_window = Toplevel(app)
    popup_window.geometry(f"{width}x{height}")
    popup_window.title("File Transfer Status")
    popup_window.attributes("-topmost", True)
    image = PhotoImage(file=image_file)
    label = Label(popup_window, image=image)
    label.image = image
    label.pack()
    
    # Store green popup reference if this is the green popup
    if is_green:
        green_popup = popup_window
    
    return popup_window

def hide_popup(popup_window):
    if popup_window:
        popup_window.destroy()

# New method to delete .bin files in selected machines' destination directories
def delete_bin_files():
    selected_machines = [machine_num for machine_num, var in machine_states.items() if var.get() == 1]
    if not selected_machines:
        messagebox.showinfo("Info", "No machines selected. Please select machines before attempting to delete .bin files.")
        return

    bin_files_deleted = 0
    for machine_num in selected_machines:
        # Get the directory associated with the selected machine number
        if machine_num <= len(destination_directories):
            directory = destination_directories[machine_num - 1]
            for file_path in directory.glob("*.bin"):
                try:
                    os.remove(file_path)
                    bin_files_deleted += 1
                except Exception as e:
                    messagebox.showerror("Error", f"Error deleting {file_path}: {e}")

    if bin_files_deleted > 0:
        messagebox.showinfo("Success", f"Deleted {bin_files_deleted} .bin files from selected machines.")
    else:
        messagebox.showinfo("Info", "No .bin files found on selected machines.")
    transfer_button.configure(state="enabled")

# Function for the back button to return to Frame 2
def back_to_frame2():
    global fileErrors
    fileErrors.clear()  # Clear fileErrors when navigating back to Frame 2
    switch_frame(frame2)


# Add the Transfer Files button and Back button at the bottom of Frame 3
back_button = ctk.CTkButton(
    frame3,
    text="Back",
    command=back_to_frame2,
    text_color="white"
)
back_button.grid(row=2, column=0, padx=(20, 10), pady=20, sticky="ew")

# Update the delete button in Frame 3 to use the modified delete_bin_files function
delete_button = ctk.CTkButton(
    frame3, text="Delete .bin Files from Selected Machines", command=delete_bin_files,
    fg_color="#CC0000", hover_color="#990000", text_color="white"
)
delete_button.grid(row=1, column=0, padx=(20, 10), pady=20, sticky="ew")

# Update Transfer Files button to use new concurrent transfer logic
transfer_button = ctk.CTkButton(
    frame3, text="Transfer Files to Machines", command=transfer_files_to_machines,
    fg_color="#008000", hover_color="#006400", text_color="white"
)
transfer_button.grid(row=1, column=1, padx=(10, 20), pady=20, sticky="ew")

# Configure columns to have equal weight for even distribution
frame3.grid_columnconfigure(0, weight=1)
frame3.grid_columnconfigure(1, weight=1)

# Start with Frame 1 visible
switch_frame(frame1)

# Run the application
app.mainloop()
