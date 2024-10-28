import customtkinter as ctk
from tkinter import filedialog, messagebox  # Corrected import
import os
from PIL import Image, ImageTk, ImageOps
import shutil

# Initialize the customtkinter appearance
ctk.set_appearance_mode("dark")  # Modes: "System" (default), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (default), "green", "dark-blue")

# Create the main window
app = ctk.CTk()
app.title("Machine Staging")
app.geometry("600x900")
app.maxsize(600, app.winfo_screenheight())

# Function to switch frames
def switch_frame(frame):
    frame.tkraise()

# Frame 1 - Machine Selection
frame1 = ctk.CTkFrame(app, width=400, height=500)
frame1.grid(row=0, column=0, sticky="nsew", padx=(20, 0), pady=(20, 0))

# Frame 2 - File Uploads (One Column Layout)
frame2 = ctk.CTkFrame(app, width=400, height=500)
frame2.grid(row=0, column=0, sticky="nsew", padx=(40, 0), pady=(20, 0))

# Frame 3 - Scrollable Frame for File Assignment Display
frame3 = ctk.CTkFrame(app, width=400, height=500)
frame3.grid(row=0, column=0, sticky="nsew", padx=(40, 0), pady=(20, 0))

# ---- Frame 1: Machine Selection ----

# Function to select all machines
def select_all_machines():
    for machine_num in range(1, 12):  # Machines 1 to 11
        machine_states[machine_num].set(1)  # Set the checkbox variable to 1 (checked)
        update_image_funcs[machine_num]()   # Update the image

# Create the "Select All Machines" button
select_all_button = ctk.CTkButton(
    frame1, text="Select All Machines", command=select_all_machines
)
select_all_button.grid(row=6, column=1, columnspan=2, pady=1)

# Label for the page
label1 = ctk.CTkLabel(frame1, text="Select Machines to Stage", font=("Arial", 20))
label1.grid(row=7, column=1, columnspan=2, pady=1)

from PIL import Image, ImageTk, ImageOps

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
machine_states = {}        # Dictionary to store IntVars
machine_labels = {}        # Dictionary to store image labels
update_image_funcs = {}    # Dictionary to store update functions

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

        # Create the image label
        image_label = ctk.CTkLabel(frame1, image=machine_images[machine_num]['normal'], text="")
        image_label.grid(row=row_index*2-1, column=col_index, padx=20, pady=1)
        machine_labels[machine_num] = image_label  # Store the label
        image_label.image = machine_images[machine_num]['normal']  # Keep a reference to prevent garbage collection

        # Define the command function for the checkbox
        update_image_func = make_update_image(machine_num)
        update_image_funcs[machine_num] = update_image_func  # Store the update function

        # Create the checkbox under the image
        checkbox = ctk.CTkCheckBox(frame1, text=f"Machine {machine_num}", variable=var, command=update_image_func)
        checkbox.grid(row=row_index*2, column=col_index, padx=20, pady=0, sticky="n")

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

# Button to go to the next page (frame2)
next_button = ctk.CTkButton(frame1, text="Submit", command=lambda: switch_frame(frame2))
next_button.grid(row=(len(layout)*2 + 3), column=1, columnspan=2, pady=10, sticky='we')

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

# Place widgets inside the scrollable frame

# Upload Envelope Files Button
upload_envelope_button = ctk.CTkButton(
    scrollable_frame2, text="Select Envelope Files", command=upload_envelope_files
)
upload_envelope_button.grid(row=0, column=0, padx=20, pady=10, sticky="ew", columnspan=2)

# Envelope Files Label Title
envelope_label_title = ctk.CTkLabel(
    scrollable_frame2, text="Selected Envelope Files", font=("Arial", 14)
)
envelope_label_title.grid(row=1, column=0, padx=20, pady=5, sticky="ew", columnspan=2)

# Envelope Files Label (Scrollable if content exceeds frame)
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
clear_envelope_button.grid(row=3, column=0, padx=20, pady=5, sticky="ew", columnspan=2)

# Upload Letter Files Button
upload_letter_button = ctk.CTkButton(
    scrollable_frame2, text="Select Letter Files", command=upload_letter_files
)
upload_letter_button.grid(row=4, column=0, padx=20, pady=10, sticky="ew", columnspan=2)

# Letter Files Label Title
letter_label_title = ctk.CTkLabel(
    scrollable_frame2, text="Selected Letter Files", font=("Arial", 14)
)
letter_label_title.grid(row=5, column=0, padx=20, pady=5, sticky="ew", columnspan=2)

# Letter Files Label (Scrollable if content exceeds frame)
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
clear_letter_button.grid(row=7, column=0, padx=20, pady=5, sticky="ew", columnspan=2)

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
back_button.grid(row=9, column=0, padx=20, pady=10, sticky="ew", columnspan=2)

# ---- Frame 3: Scrollable File Assignment Display ----

# Configure frame3 to expand and hold the scrollable frame and buttons
frame3.grid_rowconfigure(0, weight=1)
frame3.grid_columnconfigure(0, weight=1)
frame3.grid_columnconfigure(1, weight=1)

# Place the scrollable frame in frame3
scrollable_frame = ctk.CTkScrollableFrame(frame3)
scrollable_frame.grid(row=0, column=0, columnspan=2, padx=20, pady=20, sticky="nsew")

# Global variable to store file assignments
file_assignments = []  # List of tuples: (machine number, file path)

def display_file_assignments():
    global file_assignments
    file_assignments = []  # Clear previous assignments

    for widget in scrollable_frame.winfo_children():  # Clear previous widgets
        widget.destroy()

    selected_machines = sorted([machine_num for machine_num, var in machine_states.items() if var.get() == 1])

    # Determine which files are uploaded
    if envelope_files:
        all_files = envelope_files
        file_type = "Envelope"
    elif letter_files:
        all_files = letter_files
        file_type = "Letter"
    else:
        all_files = []
        file_type = "No"

    # Assign one file per selected machine
    for index, machine in enumerate(selected_machines):
        if index < len(all_files):
            file_path = all_files[index]
            file_name = os.path.basename(file_path)
            # Store the assignment
            file_assignments.append((machine, file_path))
        else:
            file_name = "No file assigned"
            file_path = None
            # Store the assignment with None file_path
            file_assignments.append((machine, file_path))

        # Create the label text with one file per machine
        label_text = f"Machine {machine}: {file_name}"

        assignment_label = ctk.CTkLabel(
            scrollable_frame,
            text=label_text,
            font=("Arial", 12)
        )
        assignment_label.grid(row=index, column=0, padx=10, pady=5, sticky="w")

# Function to get the local folder path for a machine
def get_machine_folder_path(machine_num):
    base_path = r"C:\Users\James\AppData\Roaming\Microsoft\Windows\Network Shortcuts"
    folder_name = f"Machine-{machine_num:02d}"  # Zero-padded machine number
    machine_folder_path = os.path.join(base_path, folder_name)
    return machine_folder_path

# Modified function to transfer files to machines
def transfer_files_to_machines():
    for machine_num, file_path in file_assignments:
        if file_path is None:
            # No file assigned to this machine
            continue
        # Get the local machine folder path
        destination_folder = get_machine_folder_path(machine_num)
        if not os.path.exists(destination_folder):
            messagebox.showerror("Error", f"Destination folder does not exist for Machine {machine_num}:\n{destination_folder}")
            continue

        # Before transferring the new file, delete any .bin files in the destination folder
        try:
            # List all files in the destination folder
            for filename in os.listdir(destination_folder):
                if filename.endswith(".bin"):
                    file_to_delete = os.path.join(destination_folder, filename)
                    os.remove(file_to_delete)
                    print(f"Deleted existing .bin file: {file_to_delete}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete existing .bin files in Machine {machine_num}'s folder:\n{e}")
            continue

        # Now proceed to copy the new file
        destination_path = os.path.join(destination_folder, os.path.basename(file_path))
        try:
            # Copy the file
            shutil.copy2(file_path, destination_path)
            print(f"Copied {file_path} to {destination_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to copy file to Machine {machine_num}:\n{e}")
            continue
    messagebox.showinfo("Success", "Files have been transferred to the machines.")

# Function for the back button to return to Frame 2
def back_to_frame2():
    switch_frame(frame2)

# Add the Transfer Files button and Back button at the bottom of Frame 3
back_button = ctk.CTkButton(frame3, text="Back", command=back_to_frame2)
back_button.grid(row=1, column=0, padx=(20, 10), pady=20, sticky="ew")

transfer_button = ctk.CTkButton(
    frame3,
    text="Transfer Files to Machines",
    command=transfer_files_to_machines,
    fg_color="#008000",  # Green color
    hover_color="#006400",
    text_color="white"
)
transfer_button.grid(row=1, column=1, padx=(10, 20), pady=20, sticky="ew")

# Configure columns to have equal weight for even distribution
frame3.grid_columnconfigure(0, weight=1)
frame3.grid_columnconfigure(1, weight=1)

# Start with Frame 1 visible
switch_frame(frame1)

# Run the application
app.mainloop()
