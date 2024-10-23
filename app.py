import customtkinter as ctk
from tkinter import filedialog
import os

# Initialize the customtkinter appearance
ctk.set_appearance_mode("dark")  # Modes: "System" (default), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (default), "green", "dark-blue")

# Create the main window
app = ctk.CTk()
app.title("Machine Staging")
app.geometry("550x560")

# Function to switch frames
def switch_frame(frame):
    frame.tkraise()

# Frame 1 - Machine Selection
frame1 = ctk.CTkFrame(app, width=400, height=500)
frame1.grid(row=0, column=0, sticky="nsew", padx=(40,0))

# Frame 2 - File Uploads (One Column Layout)
frame2 = ctk.CTkFrame(app, width=400, height=500)
frame2.grid(row=0, column=0, sticky="nsew", padx=(40,0))

# Frame 3 - Scrollable Frame for File Assignment Display
frame3 = ctk.CTkFrame(app, width=400, height=500)
frame3.grid(row=0, column=0, sticky="nsew", padx=(40,0))

# ---- Frame 1: Machine Selection ----

# Label for the page
label1 = ctk.CTkLabel(frame1, text="Select Machines to Stage", font=("Arial", 20))
label1.grid(row=0, column=0, columnspan=3, pady=20)

# Variables to hold the state of the checkboxes (selected/unselected)
machine_states = [ctk.StringVar(value="off") for _ in range(30)]

# Create checkboxes for selecting machines in a grid layout (3 columns, 10 rows)
for i in range(30):
    row = (i % 10) + 1  # Row index (start from 1 to leave space for the label)
    col = i // 10  # Column index (0 to 2)
    checkbox = ctk.CTkCheckBox(frame1, text=f"Machine {i+1}", variable=machine_states[i], onvalue="on", offvalue="off")
    checkbox.grid(row=row, column=col, padx=20, pady=5, sticky="w")

# Button to go to the next page (frame2)
next_button = ctk.CTkButton(frame1, text="Submit", command=lambda: switch_frame(frame2))
next_button.grid(row=11, column=1, pady=20)

# ---- Frame 2: File Uploads (One Column Layout) ----

# Variables to store selected file paths
envelope_files = []
letter_files = []

# Function to upload envelope files
def upload_envelope_files():
    global envelope_files
    envelope_files = filedialog.askopenfilenames(title="Select Envelope Files")
    envelope_label.configure(text="\n".join([os.path.basename(f) for f in envelope_files]) if envelope_files else "No files selected")

# Function to upload letter files
def upload_letter_files():
    global letter_files
    letter_files = filedialog.askopenfilenames(title="Select Letter Files")
    letter_label.configure(text="\n".join([os.path.basename(f) for f in letter_files]) if letter_files else "No files selected")

# Upload Buttons and File Display (Single Column)
upload_envelope_button = ctk.CTkButton(frame2, text="Select Envelope Files", command=upload_envelope_files)
upload_envelope_button.grid(row=0, column=1, padx=20, pady=20, sticky="ew")

envelope_label_title = ctk.CTkLabel(frame2, text="Selected Envelope Files", font=("Arial", 14))
envelope_label_title.grid(row=1, column=1, padx=20, pady=10, sticky="ew")

envelope_label = ctk.CTkLabel(frame2, text="No files selected", font=("Arial", 12))
envelope_label.grid(row=2, column=1, padx=20, pady=10, sticky="ew")

upload_letter_button = ctk.CTkButton(frame2, text="Select Letter Files", command=upload_letter_files)
upload_letter_button.grid(row=3, column=1, padx=20, pady=20, sticky="ew")

letter_label_title = ctk.CTkLabel(frame2, text="Selected Letter Files", font=("Arial", 14))
letter_label_title.grid(row=4, column=1, padx=20, pady=10, sticky="ew")

letter_label = ctk.CTkLabel(frame2, text="No files selected", font=("Arial", 12))
letter_label.grid(row=5, column=1, padx=20, pady=10, sticky="ew")

# Submit button to go to the third frame and display assigned files
submit_button_frame2 = ctk.CTkButton(frame2, text="Submit", command=lambda: [display_file_assignments(), switch_frame(frame3)])
submit_button_frame2.grid(row=6, column=1, padx=20, pady=20, sticky="ew")

# Back Button to return to Frame 1
back_button = ctk.CTkButton(frame2, text="Back", command=lambda: switch_frame(frame1))
back_button.grid(row=7, column=1, padx=20, pady=30, sticky="ew")

# ---- Frame 3: Scrollable File Assignment Display ----

scrollable_frame = ctk.CTkScrollableFrame(frame3, width=400, height=500)
scrollable_frame.grid(row=0, column=0, padx=20, pady=20)

# Function to display the file assignments to selected machines
def display_file_assignments():
    for widget in scrollable_frame.winfo_children():  # Clear previous widgets
        widget.destroy()

    selected_machines = [i for i, state in enumerate(machine_states) if state.get() == "on"]

    # Combine envelope and letter files into one list
    all_files = envelope_files + letter_files

    # Assign one file per selected machine
    for index, machine in enumerate(selected_machines):
        if index < len(all_files):
            file_name = os.path.basename(all_files[index])
        else:
            file_name = "No file assigned"

        # Create the label text with one file per machine
        label_text = f"Machine {machine + 1}: {file_name}"

        assignment_label = ctk.CTkLabel(
            scrollable_frame, 
            text=label_text, 
            font=("Arial", 12)
        )
        assignment_label.grid(row=index, column=0, padx=10, pady=5, sticky="w")

# Start with Frame 1 visible
switch_frame(frame1)

# Run the application
app.mainloop()
