import tkinter as tk
from tkinter import ttk, messagebox
import cv2
from PIL import Image, ImageTk

class MainScreen:
    # --- Initialize the main screen GUI ---
    def __init__(self, root):
        self.root = root
        self.root.title("ErgoScan - Main Screen") #title
        self.root.geometry("1200x800") #resolution of window
        self.root.configure(bg="#f0f0f0") #background color
        
    
        # Initialize webcam variables
        self.cap = None
        self.webcam_active = True  # Set to True initially since we want camera on by default
        self.start_button = tk.Button(self.root, text="Start", state="disabled")
        self.calibrated = False  #state variable to track if calibration has been done or not
        
        # Calling setup functions to initialize UI and webcam
        self.setup_ui()
        self.start_webcam_preview()

    # --- Function that sets up the UI (split into left and right sections) ---
    def setup_ui(self):
        # Configure the root layout grid and weight
        self.root.grid_columnconfigure(0, weight=1) #configure column 0 for left section
        self.root.grid_columnconfigure(1, weight=1) #configure column 1 for right section
        self.root.grid_rowconfigure(0, weight=1)
        
        # --- Creating Frames --- 
        #Left section frame
        self.left_frame = tk.Frame(self.root, bg="#ffffff")
        self.left_frame.grid(row=0, column=0, sticky="nsew", padx=(10, 5), pady=10)

        #Right section frame
        self.right_frame = tk.Frame(self.root, bg="#ffffff")
        self.right_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 10), pady=10)
        
        # --- Call set up functions for each section ---
        #Left Section - Form and Icons
        self.setup_left_section()

        #Right Section - Webcam Display
        self.setup_right_section()


    # ---------- LEFT SECTION BELOW ----------

    # --- Modular function that builds the left side of the screen ---
    def setup_left_section(self):
        # Configure the left frame layout and grid weight
        self.left_frame.grid_rowconfigure(0, weight=1)
        self.left_frame.grid_columnconfigure(1, weight=1)
        
        # Left icons column
        icons_frame = tk.Frame(self.left_frame, bg="#ffffff", width=60)
        icons_frame.grid(row=0, column=0, sticky="ns", padx=(10, 5), pady=10)
        icons_frame.grid_propagate(False)
        
        # Settings icon button (top)
        settings_button = tk.Button(icons_frame, text="⚙️", font=("Arial", 24),
            bg="#ffffff", bd=0, command=self.open_settings,
            cursor="hand2", width=2, height=1,
            activebackground="#ffffff", highlightthickness=0,
            relief="flat")
        settings_button.pack(pady=(10, 5))
        
        # Profile icon button (below settings)
        profile_button = tk.Button(icons_frame, text="👤", font=("Arial", 24),
            bg="#ffffff", bd=0, command=self.open_profile,
            cursor="hand2", width=2, height=1,
            activebackground="#ffffff", highlightthickness=0,
            relief="flat")
        profile_button.pack(pady=5)
        
        # Main content area
        content_frame = tk.Frame(self.left_frame, bg="#ffffff")
        content_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 10), pady=10)
        content_frame.grid_rowconfigure(1, weight=1)
        content_frame.grid_columnconfigure(0, weight=1)
        
        # Title
        title_label = tk.Label(content_frame, text="Patient Information", 
                              font=("Arial", 18, "bold"), bg="#ffffff")
        title_label.grid(row=0, column=0, pady=(0, 10))
        
        # Form frame
        form_frame = tk.Frame(content_frame, bg="#ffffff")
        form_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        form_frame.grid_columnconfigure(1, weight=1)
        
        # Form fields with dummy data
        fields = [
            ("Full Name:", "John Smith"),
            ("Age:", "28"),
            ("Height (cm):", "175"),
            ("Weight (kg):", "70"),
            ("Occupation:", "Software Developer"),
            ("Email:", "john.smith@email.com"),
            ("Phone:", "(555) 123-4567"),
            ("Medical History:", "No significant medical history"),
            ("Current Symptoms:", "Lower back pain, neck stiffness"),
            ("Exercise Frequency:", "3 times per week")
        ]
        
        for i, (label_text, default_value) in enumerate(fields):
            # Label
            label = tk.Label(form_frame, text=label_text, font=("Arial", 11, "bold"), 
                           bg="#ffffff", anchor="w")
            label.grid(row=i, column=0, sticky="w", pady=5, padx=(0, 10))
            
            # Entry field
            if label_text in ["Medical History:", "Current Symptoms:"]:
                # Text widget for longer text
                text_widget = tk.Text(form_frame, height=3, width=40, font=("Arial", 10),
                                    relief="solid", bd=1)
                text_widget.grid(row=i, column=1, sticky="ew", pady=5)
                text_widget.insert("1.0", default_value)
            else:
                # Regular entry
                entry = tk.Entry(form_frame, font=("Arial", 10), relief="solid", bd=1)
                entry.grid(row=i, column=1, sticky="ew", pady=5)
                entry.insert(0, default_value)
        
        # Submit button
        submit_button = tk.Button(form_frame, text="Save Information",
                                font=("Arial", 12, "bold"), bg="#2196F3", fg="white",
                                width=20, height=2, command=self.save_form,
                                relief="raised", bd=2, activebackground="#1976D2",
                                activeforeground="white", highlightthickness=0)
        submit_button.grid(row=len(fields), column=0, columnspan=2, pady=20)

    def setup_form(self):
        """Set up the form in the right section"""
        # Form frame
        form_frame = tk.Frame(self.right_frame, bg="#ffffff", relief="groove", bd=2)
        form_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        form_frame.grid_columnconfigure(1, weight=1)
        
        # Form fields
        fields = [
            ("Name:", "name"),
            ("Age:", "age"),
            ("Height (cm):", "height"),
            ("Weight (kg):", "weight"),
            ("Occupation:", "occupation"),
            ("Workspace Type:", "workspace")
        ]
        
        self.form_vars = {}
        
        for i, (label_text, var_name) in enumerate(fields):
            # Label
            label = tk.Label(form_frame, text=label_text, font=("Arial", 12),
                           bg="#ffffff", anchor="w")
            label.grid(row=i, column=0, sticky="w", padx=10, pady=8)
            
            # Entry
            self.form_vars[var_name] = tk.StringVar()
            entry = tk.Entry(form_frame, textvariable=self.form_vars[var_name],
                           font=("Arial", 12), width=25)
            entry.grid(row=i, column=1, sticky="ew", padx=10, pady=8)
        
        # Buttons frame
        buttons_frame = tk.Frame(form_frame, bg="#ffffff")
        buttons_frame.grid(row=len(fields), column=0, columnspan=2, pady=20)
        
        # Save button
        save_button = tk.Button(buttons_frame, text="Save Information",
                               font=("Arial", 12, "bold"), bg="#2196F3", fg="white",
                               width=15, height=1, command=self.save_form,
                               relief="raised", bd=2)
        save_button.pack(side="left", padx=10)
        
        # Clear button
        clear_button = tk.Button(buttons_frame, text="Clear Form",
                               font=("Arial", 12), bg="#f44336", fg="white",
                               width=15, height=1, command=self.clear_form,
                               relief="raised", bd=2)
        clear_button.pack(side="left", padx=10)
    
        
    def open_settings(self):
        """Handle settings button click"""
        print("Opening settings page...")
        # TODO: Implement navigation to settings page
        tk.messagebox.showinfo("Settings", "Opening settings page...")
        
    def open_profile(self):
        """Handle profile button click"""
        print("Opening profile page...")
        # TODO: Implement navigation to profile page
        tk.messagebox.showinfo("Profile", "Opening profile page...")
        
    def save_form(self):
        """Handle form save"""
        print("Saving patient information...")
        # TODO: Implement actual data saving logic
        tk.messagebox.showinfo("Success", "Patient information saved successfully!")
        
    def clear_form(self):
        """Clear all form fields"""
        print("Clearing patient information form...")
        # TODO: Implement form clearing logic
        tk.messagebox.showinfo("Cleared", "Form cleared successfully!")
        
    def on_closing(self):
        """Handle window closing"""
        if self.cap:
            self.cap.release()
        self.root.destroy()

        
    # ---------- RIGHT SECTION BELOW ----------

    # --- Modular function that builds the right side of the screen ---
    def setup_right_section(self):
        # Configure the right frame layout and grid weight
        self.right_frame.grid_rowconfigure(1, weight=1)
        self.right_frame.grid_columnconfigure(0, weight=1)
        
        # Title for right section
        title_label = tk.Label( #Defines the title label details
            self.right_frame, 
            text="Webcam Preview", 
            font=("Arial", 16, "bold"), 
            bg="#ffffff"
        )
        title_label.grid( #Defines the grid placement of the title label
            row=0, 
            column=0, 
            pady=(10, 5), 
            sticky="n"
        )
        
        # --- Webcam Preview Display Area ---
        # Webcam frame details
        self.webcam_frame = tk.Frame( 
            self.right_frame, 
            bg="#000000", 
            width=600, 
            height=450, 
            relief="sunken", 
            bd=2
        )
        # Webcam frame grid placement
        self.webcam_frame.grid(
            row=1, 
            column=0, 
            padx=20, 
            pady=10, 
            sticky="nsew"
        )
        self.webcam_frame.grid_propagate(False) #Disable automatic frame resizing
        
        # Webcam label for displaying video feed
        # Create initial blank image to maintain consistent size
        initial_blank = Image.new('RGB', (580, 430), color='black')
        initial_photo = ImageTk.PhotoImage(initial_blank)
        
        self.webcam_label = tk.Label( #webcam label details
            self.webcam_frame, 
            bg="#000000",             
            image=initial_photo,
            text="Initializing camera...", 
            fg="white",
            font=("Arial", 14),
            compound='center'  # Show text over image
        )
        self.webcam_label.image = initial_photo  # Keep reference to prevent garbage collection
        self.webcam_label.pack(expand=True, fill="both") #Enable automatic resizing for the label


        # --- Toggle webcam ON/OFF switch details & grid placement ---
        self.toggle_camera_switch = ToggleSwitch( #toggle switch details using ToggleSwitch class
            self.right_frame, 
            command=self.on_camera_toggle, 
            initial_state=self.webcam_active, #intial state based on webcam_active variable
            bg="#ffffff"
        )
        self.toggle_camera_switch.grid( #grid placement
            row=2, 
            column=0, 
            pady=(5, 25), 
            sticky="n"
        )

        # --- Start scanning/calibration buttons --- 
        button_frame = tk.Frame(self.right_frame, bg="#ffffff") #init button frame
        button_frame.grid(row=3, column=0, pady=(10, 20), sticky="n") #define button frame grid placement

        # Start calibration button
        self.calibration_button = tk.Button( #start calibration button details
            button_frame,
            text="Start Calibration",
            font=("Arial", 14),
            bg="#2196F3",
            fg="white",
            width=20,
            height=2,
            command = self.start_calibration, # call function on click
            relief="raised",
            bd=3,
            activebackground="#2196F3",  # Same as normal background
            activeforeground="white",
            highlightthickness=0,
            highlightcolor="#2196F3",     # Remove highlight color
            highlightbackground="#2196F3", # Remove highlight background
            takefocus=False               # Prevent taking focus
        )
        self.calibration_button.grid(row=4, column=0, pady=(10, 5), sticky="n") #start calibration button grid placement

        # Start scanning button 
        self.start_button = tk.Button( #start scanning button details
            button_frame, 
            text="Start Scanning",
            font=("Arial", 14), 
            bg="#4CAF50", 
            fg="white",
            width=20, 
            height=2, 
            command = self.start_scanning, #call function on click
            relief="raised", 
            bd=3,
            activebackground="#4CAF50",   # Same as normal background
            activeforeground="white",
            highlightthickness=0,
            highlightcolor="#4CAF50",     # Remove highlight color
            highlightbackground="#4CAF50", # Remove highlight background
            takefocus=False               # Prevent taking focus
        )
        self.start_button.grid(row=5, column=0, pady=(5, 10), sticky="n") #start scanning button grid placement


    # --- Toggle webcam ON/OFF function ---
    def on_camera_toggle(self, state):
        if state:
            print("Camera ON")
            self.start_webcam_preview()
        else:
            print("Camera OFF")
            self.stop_webcam()


    # --- Start calibration & scanning functions ---
    def start_webcam_preview(self):
        try:
            self.cap = cv2.VideoCapture(0)
            if self.cap.isOpened():
                self.webcam_active = True
                self.update_webcam()
            else:
                self.webcam_label.config(text="Camera not available", fg="red")
        except Exception as e:
            self.webcam_label.config(text=f"Camera error: {str(e)}", fg="red")
            
    def update_webcam(self):
        if self.webcam_active and self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                # Resize frame to fit the display area
                frame = cv2.resize(frame, (580, 430))
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Convert to PhotoImage
                image = Image.fromarray(frame)
                photo = ImageTk.PhotoImage(image)
                
                # Update label
                self.webcam_label.config(image=photo, text="")
                self.webcam_label.image = photo
                
            # Schedule next update
            self.root.after(30, self.update_webcam)

    def stop_webcam(self):
        """Safely stop the webcam feed and release resources."""
        if self.webcam_active:
            self.webcam_active = False  # stop update loop

        if hasattr(self, "cap") and self.cap and self.cap.isOpened():
            self.cap.release()
            self.cap = None

        # Create a blank image with the same dimensions as the camera feed
        blank_image = Image.new('RGB', (580, 430), color='black')
        blank_photo = ImageTk.PhotoImage(blank_image)
        
        # Update label with blank image and overlay text
        self.webcam_label.config(
            image=blank_photo, 
            text="Camera OFF", 
            fg="white", 
            compound='center', 
            font=("Arial", 16)
        )
        self.webcam_label.image = blank_photo

        # Update toggle button color to red
        if hasattr(self, "toggle_camera_button"):
            self.toggle_camera_button.config(bg="#f44336")
        
        print("Webcam stopped and resources released.")


    # --- Start calibration & scanning functions ---
    def start_calibration(self):
        """Start calibration process"""
        print("Starting calibration...")
        tk.messagebox.showinfo("Calibration", "Calibration started")
        
    def start_scanning(self):
        """Handle start scanning button click"""
        print("Navigating to camera page...")
        # TODO: Implement navigation to camera page
        # This could involve opening a new window or switching frames
        tk.messagebox.showinfo("Start Scanning", "Scanning Started")


    # --- Class for Webcam ON/OFF iOS toggle switch look ---
class ToggleSwitch(tk.Frame):
    def __init__(self, parent, command=None, **kwargs):

        self.state = kwargs.pop('initial_state', False)
        self.command = command
        super().__init__(parent, **kwargs)

        self.canvas = tk.Canvas(self, width=60, height=30, bg=self["bg"], highlightthickness=0)
        self.canvas.pack()
        self.rect = self.canvas.create_oval(
            5, 5, 25, 25, 
            fill="white", 
            outline=""
        )
        self.bg_rect = self.canvas.create_rectangle(
            0, 0, 60, 30, 
            outline="", 
            fill="#f44336"
        )
        self.canvas.tag_lower(self.bg_rect)
        self.canvas.bind("<Button-1>", self.toggle)

        # Set initial visual state
        if self.state:
            self.canvas.itemconfig(self.bg_rect, fill="#50ff36")
            self.canvas.move(self.rect, 30, 0)

    def toggle(self, event=None):
        self.state = not self.state
        if self.state:
            self.canvas.itemconfig(self.bg_rect, fill="#50ff36")
            self.canvas.move(self.rect, 30, 0)
        else:
            self.canvas.itemconfig(self.bg_rect, fill="#f44336")
            self.canvas.move(self.rect, -30, 0)
        if self.command:
            self.command(self.state)


if __name__ == "__main__":
    root = tk.Tk()
    app = MainScreen(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()