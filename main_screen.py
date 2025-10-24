import tkinter as tk
from tkinter import ttk, messagebox
import cv2
from PIL import Image, ImageTk
from calibration import BodyCalibrationInstructions
from ergoscan_settings import ErgoScanSettings


class MainScreen:
    # --- Initialize the main screen GUI ---
    def __init__(self, root):
        self.root = root
        self.root.title("ErgoScan - Main Screen") #title
        self.root.geometry("1200x800") #resolution of window
        self.root.configure(bg="#f0f0f0") #background color
        
        # Initialize webcam variables
        self.cap = None
        # Start the app with camera OFF by default
        self.webcam_active = False
        self.start_button = tk.Button(self.root, text="Start", state="disabled")
        self.calibrated = False  #state variable to track if calibration has been done or not
        
        # Initialize profile data for name display
        self.profile_name = "John Doe"
        
        # Calling setup functions to initialize UI. Do NOT start webcam automatically.
        self.setup_ui()

    # --- Function that sets up the UI (split into left and right sections) ---
    def setup_ui(self):
        # Configure the root layout grid and weight
        self.root.grid_columnconfigure(1, weight=1) #configure column 1 for form section
        self.root.grid_columnconfigure(2, weight=1) #configure column 2 for right section
        self.root.grid_rowconfigure(0, weight=1)
        
        # Create top-left icons frame
        self.icons_frame = tk.Frame(self.root, bg="#f0f0f0")
        self.icons_frame.grid(row=0, column=0, sticky="nw", padx=10, pady=10)
        
        # --- Creating Frames --- 
        #Left section frame (now for form)
        self.left_frame = tk.Frame(self.root, bg="#ffffff")
        self.left_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 5), pady=10)

        #Right section frame
        self.right_frame = tk.Frame(self.root, bg="#ffffff")
        self.right_frame.grid(row=0, column=2, sticky="nsew", padx=(5, 10), pady=10)
        
        # --- Call set up functions for each section ---
        #Setup icons section
        self.setup_icons_section()
        
        #Left Section - Form
        self.setup_left_section()

        #Right Section - Webcam Display
        self.setup_right_section()


    # --- Setup icons section (profile and settings) ---
    def setup_icons_section(self):
        # Profile icon with name
        profile_frame = tk.Frame(self.icons_frame, bg="#f0f0f0")
        profile_frame.pack(pady=(0, 10), anchor="w")
        
        profile_icon = tk.Button(profile_frame, text="👤", font=("Arial", 16), bg="#e0e0e0", 
                                 command=self.open_profile, relief="flat", width=3)
        profile_icon.pack(side="left")
        
        profile_label = tk.Label(profile_frame, text=self.profile_name, font=("Arial", 10), 
                                 bg="#f0f0f0", fg="#333333")
        profile_label.pack(side="left", padx=(5, 0))
        
        # Settings icon
        settings_icon = tk.Button(self.icons_frame, text="⚙", font=("Arial", 16), bg="#e0e0e0", 
                                  command=self.show_settings, relief="flat", width=3)
        settings_icon.pack(pady=(0, 10), anchor="w")

    # ---------- LEFT SECTION BELOW ----------

    # --- Modular function that builds the left side of the screen ---
    def setup_left_section(self):
        # Configure the left frame layout and grid weight
        self.left_frame.grid_rowconfigure(0, weight=1)
        self.left_frame.grid_columnconfigure(0, weight=1)
        
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
        profile_button.pack(pady=(10, 5))
        
        # Main content area
        content_frame = tk.Frame(self.left_frame, bg="#ffffff")
        content_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        content_frame.grid_rowconfigure(1, weight=1)
        content_frame.grid_columnconfigure(0, weight=1)
        
        # Title
        title_label = tk.Label(content_frame, text="Body Measurements", 
                              font=("Arial", 18, "bold"), bg="#ffffff")
        title_label.grid(row=0, column=0, pady=(0, 10))
        
        # Form frame
        form_frame = tk.Frame(content_frame, bg="#ffffff")
        form_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        form_frame.grid_columnconfigure(1, weight=1)
        
        # Form fields with body measurements
        fields = [
            ("Shoulder Width (cm):", "45"),
            ("Torso Length (cm):", "60"),
            ("Hip Width (cm):", "38"),
            ("Arm Length (cm):", "65"),
            ("Leg Length (cm):", "85")
        ]
        
        for i, (label_text, default_value) in enumerate(fields):
            # Label
            label = tk.Label(form_frame, text=label_text, font=("Arial", 11, "bold"), 
                           bg="#ffffff", anchor="w")
            label.grid(row=i, column=0, sticky="w", pady=5, padx=(0, 10))
            
            # Entry field
            entry = tk.Entry(form_frame, font=("Arial", 10), relief="solid", bd=1)
            entry.grid(row=i, column=1, sticky="ew", pady=5)
            entry.insert(0, default_value)
        
        # Submit button
        submit_button = tk.Button(form_frame, text="Save Measurements",
                                font=("Arial", 12, "bold"), bg="#2196F3", fg="white",
                                width=20, height=2, command=self.save_form,
                                relief="raised", bd=2, activebackground="#1976D2",
                                activeforeground="white", highlightthickness=0)
        submit_button.grid(row=len(fields), column=0, columnspan=2, pady=20)

    def open_profile(self):
        """Handle profile button click - allows changing profile name"""
        print("Changing profile name...")
        
        # Create a simple dialog to change profile name
        dialog = tk.Toplevel(self.root)
        dialog.title("Edit Profile")
        dialog.geometry("300x150")
        dialog.configure(bg="#ffffff")
        dialog.resizable(False, False)
        
        # Center the dialog on parent window
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Main frame
        main_frame = tk.Frame(dialog, bg="#ffffff", padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = tk.Label(main_frame, text="Edit Profile Name", 
                              font=("Arial", 14, "bold"), bg="#ffffff")
        title_label.pack(pady=(0, 15))
        
        # Name input frame
        input_frame = tk.Frame(main_frame, bg="#ffffff")
        input_frame.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(input_frame, text="Name:", font=("Arial", 11), 
                bg="#ffffff").pack(side=tk.LEFT)
        
        name_var = tk.StringVar(value=self.profile_name)
        name_entry = tk.Entry(input_frame, textvariable=name_var, 
                             font=("Arial", 11), width=20)
        name_entry.pack(side=tk.RIGHT)
        name_entry.focus_set()
        name_entry.select_range(0, tk.END)
        
        # Buttons frame
        buttons_frame = tk.Frame(main_frame, bg="#ffffff")
        buttons_frame.pack()
        
        def save_profile():
            new_name = name_var.get().strip()
            if new_name:
                self.profile_name = new_name
                self.update_profile_display()
                print(f"Profile name changed to: {new_name}")
                dialog.destroy()
            else:
                tk.messagebox.showwarning("Invalid Name", "Please enter a valid name.")
        
        def cancel_profile():
            dialog.destroy()
        
        # Save button
        save_btn = tk.Button(buttons_frame, text="Save", command=save_profile,
                            font=("Arial", 10, "bold"), bg="#2196F3", fg="white",
                            width=8, relief="raised", bd=1)
        save_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Cancel button
        cancel_btn = tk.Button(buttons_frame, text="Cancel", command=cancel_profile,
                              font=("Arial", 10), bg="#f44336", fg="white",
                              width=8, relief="raised", bd=1)
        cancel_btn.pack(side=tk.LEFT)
        
        # Handle Enter key to save
        dialog.bind('<Return>', lambda e: save_profile())
        dialog.bind('<Escape>', lambda e: cancel_profile())

    def update_profile_display(self):
        """Update the profile name display in the UI"""
        # Update the profile label in the icons section if it exists
        if hasattr(self, 'icons_frame'):
            for widget in self.icons_frame.winfo_children():
                if isinstance(widget, tk.Frame):
                    for child in widget.winfo_children():
                        if isinstance(child, tk.Label) and hasattr(child, 'cget'):
                            if child.cget('text') != "👤":  # Not the icon, but the name label
                                child.configure(text=self.profile_name)

    def open_settings(self):
        """Handle settings button click"""
        print("Opening settings page...")
        
        # Check if settings window is already open
        if hasattr(self, 'settings_window') and self.settings_window.winfo_exists():
            print("Settings window is already open")
            self.settings_window.lift()  # Bring to front if already open
            return
        
        # Create a new window for settings
        self.settings_window = tk.Toplevel(self.root)
        self.settings_app = ErgoScanSettings(self.settings_window)
        
        # Set up window close event
        self.settings_window.protocol("WM_DELETE_WINDOW", self.on_settings_window_close)
        
    def save_form(self):
        """Handle form save"""
        print("Saving information...")
        # TODO: Implement actual data saving logic
        tk.messagebox.showinfo("Success", "Information saved successfully!")

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
            text="Toggle Camera ON to Start", 
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


    # --- Webcam Functions ---
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
        
        # Check if camera is active before starting calibration
        if not self.webcam_active:
            tk.messagebox.showwarning("Camera Required", "Please turn the camera on before starting calibration.")
            return
        
        # Check if calibration window is already open
        if hasattr(self, 'calibration_window') and self.calibration_window.winfo_exists():
            print("Calibration window is already open")
            return
        
        # Create a new window for calibration instructions
        self.calibration_window = tk.Toplevel(self.root)
        self.calibration_app = BodyCalibrationInstructions(self.calibration_window)
        
        # Disable the calibration button while window is open
        self.calibration_button.config(state="disabled")
        
        # Set up window close event to re-enable button
        self.calibration_window.protocol("WM_DELETE_WINDOW", self.on_calibration_window_close)
    
    def on_calibration_window_close(self):
        """Handle calibration window closing"""
        print("Calibration window closing...")
        
        # Clean up calibration app resources if it has a camera
        if hasattr(self.calibration_app, 'cap') and self.calibration_app.cap:
            self.calibration_app.cap.release()
        
        # Destroy the window
        if hasattr(self, 'calibration_window'):
            self.calibration_window.destroy()
        
        # Re-enable the calibration button
        self.calibration_button.config(state="normal")
        
    def start_scanning(self):
        """Handle start scanning button click"""
        print("Navigating to camera page...")
        # TODO: Implement navigation to camera page
        # This could involve opening a new window or switching frames
        tk.messagebox.showinfo("Start Scanning", "Scanning Started")

    def show_settings(self):
        """Handle settings icon click"""
        print("Opening settings...")
        
        # Check if settings window is already open
        if hasattr(self, 'settings_window') and self.settings_window.winfo_exists():
            print("Settings window is already open")
            self.settings_window.lift()  # Bring to front if already open
            return
        
        # Create a new window for settings
        self.settings_window = tk.Toplevel(self.root)
        self.settings_app = ErgoScanSettings(self.settings_window)
        
        # Set up window close event
        self.settings_window.protocol("WM_DELETE_WINDOW", self.on_settings_window_close)
    
    def on_settings_window_close(self):
        """Handle settings window closing"""
        print("Settings window closing...")
        
        # Destroy the window
        if hasattr(self, 'settings_window'):
            self.settings_window.destroy()

    def toggle_camera(self):
        """Toggle camera on/off"""
        if self.cap and self.cap.isOpened():
            self.cap.release()
            self.cap = None
            print("Camera turned off")
        else:
            self.cap = cv2.VideoCapture(0)
            print("Camera turned on")


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