import customtkinter as ctk

# Initialize the customtkinter appearance
ctk.set_appearance_mode("dark")  # Modes: "System" (default), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (default), "green", "dark-blue"

# Create the main window
app = ctk.CTk()
app.title("Machine Staging")
app.geometry("500x600")

# Label for the page
label = ctk.CTkLabel(app, text="Select Machines to Stage", font=("Arial", 20))
label.pack(pady=20)

# Frame to hold the checkboxes in a grid layout
frame = ctk.CTkFrame(app)
frame.pack(pady=10)

# Variables to hold the state of the checkboxes (selected/unselected)
machine_states = [ctk.StringVar(value="off") for _ in range(30)]

# Function to handle the state of each checkbox
def print_selections():
    selections = [f"Machine {i+1}: {var.get()}" for i, var in enumerate(machine_states)]
    print("Selections:", selections)

# Create checkboxes for selecting machines in a grid layout (3 columns, 10 rows)
for i in range(30):
    row = i % 10  # Row index (0 to 9)
    col = i // 10  # Column index (0 to 2)
    checkbox = ctk.CTkCheckBox(frame, text=f"Machine {i+1}", variable=machine_states[i], onvalue="on", offvalue="off")
    checkbox.grid(row=row, column=col, padx=20, pady=5, sticky="w")

# Submit button to handle the user's selection
submit_button = ctk.CTkButton(app, text="Submit", command=print_selections)
submit_button.pack(pady=20)

# Run the application
app.mainloop()
