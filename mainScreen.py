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
        self.webcam_active = False
        self.calibrated = False  #state variable to track if calibration has been done or not
        
<<<<<<< Updated upstream
        # Calling setup functions to initialize UI and webcam
=======
        # Initialize profile data
        self.profile_data = {
            "name": "John Doe",  # Placeholder name - can be edited through profile
            "email": "",
            "phone": "",
            "age": ""
        }
        
>>>>>>> Stashed changes
        self.setup_ui()
        self.start_webcam_preview()

    # --- Function that sets up the UI (split into left and right sections) ---
    def setup_ui(self):
<<<<<<< Updated upstream
        # Configure the root layout grid and weight
        self.root.grid_columnconfigure(0, weight=1) #configure column 0 for left section
        self.root.grid_columnconfigure(1, weight=1) #configure column 1 for right section
        self.root.grid_rowconfigure(0, weight=1)
        
        # --- Creating Frames --- 
        #Left section frame
        self.left_frame = tk.Frame(self.root, bg="#ffffff")
        self.left_frame.grid(row=0, column=0, sticky="nsew", padx=(10, 5), pady=10)

        #Right section frame
=======
        """Set up the main user interface"""
        # Configure grid weights for responsive design
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_columnconfigure(2, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        
        # Create top-left icons frame
        self.icons_frame = tk.Frame(self.root, bg="#f0f0f0")
        self.icons_frame.grid(row=0, column=0, sticky="nw", padx=10, pady=10)
        
        # Create left and right frames
        self.left_frame = tk.Frame(self.root, bg="#ffffff")
        self.left_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 5), pady=10)
        
>>>>>>> Stashed changes
        self.right_frame = tk.Frame(self.root, bg="#ffffff")
        self.right_frame.grid(row=0, column=2, sticky="nsew", padx=(5, 10), pady=10)
        
<<<<<<< Updated upstream
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
                                  cursor="hand2", width=2, height=1)
        settings_button.pack(pady=(10, 5))
        
        # Profile icon button (below settings)
        profile_button = tk.Button(icons_frame, text="👤", font=("Arial", 24),
                                 bg="#ffffff", bd=0, command=self.open_profile,
                                 cursor="hand2", width=2, height=1)
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
=======
        # Setup icons section
        self.setup_icons_section()
        
        # Left Section - Form
        self.setup_left_section()
        
        # Right Section - Webcam Display
        self.setup_right_section() 
        
        
    def setup_icons_section(self):
        """Set up the top-left icons section with profile and settings"""
        # Configure icons frame grid
        self.icons_frame.grid_columnconfigure(1, weight=1)
        
        # Profile icon button (on top)
        profile_button = tk.Button(self.icons_frame, text="👤", font=("Arial", 24),
                                 bg="#ffffff", bd=2, relief="raised",
                                 command=self.open_profile, cursor="hand2",
                                 width=3, height=1)
        profile_button.grid(row=0, column=0, pady=(0, 10))
        
        # Profile name display (beside the profile icon)
        self.profile_name_label = tk.Label(self.icons_frame, 
                                          text=self.profile_data["name"], 
                                          font=("Arial", 12, "bold"), 
                                          bg="#f0f0f0", fg="#2196F3",
                                          cursor="hand2", anchor="w")
        self.profile_name_label.grid(row=0, column=1, sticky="w", padx=(10, 0))
        self.profile_name_label.bind("<Button-1>", lambda e: self.open_profile())
        
        # Settings icon button (below profile)
        settings_button = tk.Button(self.icons_frame, text="⚙️", font=("Arial", 24),
                                  bg="#ffffff", bd=2, relief="raised",
                                  command=self.open_settings, cursor="hand2",
                                  width=3, height=1)
        settings_button.grid(row=1, column=0, pady=(0, 10))
        
    def setup_left_section(self):
        """Set up the left section with form"""
        # Configure left frame grid
        self.left_frame.grid_rowconfigure(1, weight=1)
        self.left_frame.grid_columnconfigure(0, weight=1)
        
        # Title
        title_label = tk.Label(self.left_frame, text="Body Measurements", 
                              font=("Arial", 18, "bold"), bg="#ffffff")
        title_label.grid(row=0, column=0, pady=(10, 0))
>>>>>>> Stashed changes
        
        # Form frame
        form_frame = tk.Frame(content_frame, bg="#ffffff")
        form_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        form_frame.grid_columnconfigure(1, weight=1)
        
        # Initialize form data dictionary for easy saving
        self.form_data = {}
        self.form_entries = {}
        
        # Form fields - body measurements
        fields = [
            ("Shoulder Width (cm):", "shoulder_width", ""),
            ("Torso Length (cm):", "torso_length", ""),
            ("Hip Width (cm):", "hip_width", ""),
            ("Arm Length (cm):", "arm_length", ""),
            ("Leg Length (cm):", "leg_length", "")
        ]
        
        for i, (label_text, field_key, default_value) in enumerate(fields):
            # Label
            label = tk.Label(form_frame, text=label_text, font=("Arial", 12, "bold"), 
                           bg="#ffffff", anchor="w")
            label.grid(row=i, column=0, sticky="w", pady=8, padx=(0, 15))
            
            # Entry field
            entry = tk.Entry(form_frame, font=("Arial", 11), relief="solid", bd=1,
                           width=20)
            entry.grid(row=i, column=1, sticky="ew", pady=8)
            if default_value:
                entry.insert(0, default_value)
            
            # Store reference for easy access
            self.form_entries[field_key] = entry
            self.form_data[field_key] = default_value
        
<<<<<<< Updated upstream
        # Submit button
        submit_button = tk.Button(form_frame, text="Save Information",
                                font=("Arial", 12, "bold"), bg="#2196F3", fg="white",
                                width=20, height=2, command=self.save_form,
                                relief="raised", bd=2)
        submit_button.grid(row=len(fields), column=0, columnspan=2, pady=20)

=======
        # Buttons frame
        buttons_frame = tk.Frame(form_frame, bg="#ffffff")
        buttons_frame.grid(row=len(fields), column=0, columnspan=2, pady=30)
        
        # Save button
        save_button = tk.Button(buttons_frame, text="Save Measurements",
                               font=("Arial", 12, "bold"), bg="#2196F3", fg="white",
                               width=18, height=2, command=self.save_form,
                               relief="raised", bd=2)
        save_button.pack(padx=10)
        
    def setup_right_section(self):
        """Set up the right section with webcam display and start scanning button"""
        # Configure right frame grid
        self.right_frame.grid_rowconfigure(1, weight=1)
        self.right_frame.grid_columnconfigure(0, weight=1)
        
        # Title for right section
        title_label = tk.Label(self.right_frame, text="Webcam Preview", 
                              font=("Arial", 16, "bold"), bg="#ffffff")
        title_label.grid(row=0, column=0, pady=(10, 5), sticky="n")
        
        # Webcam display area
        self.webcam_frame = tk.Frame(self.right_frame, bg="#000000", 
                                   width=600, height=450, relief="sunken", bd=2)
        self.webcam_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        self.webcam_frame.grid_propagate(False)
        
        # Webcam label for displaying video feed
        self.webcam_label = tk.Label(self.webcam_frame, bg="#000000", 
                                   text="Initializing camera...", fg="white",
                                   font=("Arial", 14))
        self.webcam_label.pack(expand=True, fill="both")
        
        # Start scanning button
        self.start_button = tk.Button(self.right_frame, text="Start Scanning",
                                    font=("Arial", 14, "bold"), bg="#4CAF50", fg="white",
                                    width=20, height=2, command=self.start_scanning,
                                    relief="raised", bd=3)
        self.start_button.grid(row=2, column=0, pady=20)
        
>>>>>>> Stashed changes
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
        self.webcam_label = tk.Label( #webcam label details
            self.webcam_frame, 
            bg="#000000",             
            text="Initializing camera...", 
            fg="white",
            font=("Arial", 14)
        )
        self.webcam_label.pack(expand=True, fill="both") #Enable automatic resizing for the label

        # Webcam ON/OFF toggle switch & icon
        self.toggle_camera_button = tk.Button( #toggle camera button details
            self.right_frame,
            text="ON/OFF Camera",
            font=("Arial", 12, "bold"),
            bg="#50ff36",  #color green when active
            fg="white",
            width=18,
            height=1,
            command=self.toggle_camera,
            relief="raised",
            bd=2
        )
        self.toggle_camera_button.grid(row=2, column=0, pady=(5, 25), sticky="n") #toggle camera button grid placement

        # --- Start scanning/calibration buttons --- 
        button_frame = tk.Frame(self.right_frame, bg="#ffffff") #init button frame
        button_frame.grid(row=3, column=0, pady=(10, 20)) #define button frame grid placement

        # Start calibration button
        self.calibration_button = tk.Button( #start calibration button details
            button_frame,
            text="Start Calibration",
            font=("Arial", 14, "bold"),
            bg="#2196F3",
            fg="white",
            width=20,
            height=2,
            command=self.start_calibration,
            relief="raised",
            bd=3
        )
        self.calibration_button.pack(pady=(0, 10)) #start calibration button grid placement

        # Start scanning button
        self.start_button = tk.Button( #start scanning button details
            self.right_frame, 
            text="Start Scanning",
            font=("Arial", 14, "bold"), 
            bg="#4CAF50", 
            fg="white",
            width=20, 
            height=2, 
            command = self.start_scanning,
            relief="raised", 
            bd=3
        )
        self.start_button.grid(row=2, column=0, pady=20) #start scanning button grid placement
        

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
        """Update the webcam display"""
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
        
    def start_scanning(self):
        """Handle start scanning button click"""
        print("Navigating to camera page...")
        # TODO: Implement navigation to camera page
        # This could involve opening a new window or switching frames
        tk.messagebox.showinfo("Start Scanning", "Navigating to camera page...")
<<<<<<< Updated upstream

=======
        
    def open_settings(self):
        """Handle settings button click"""
        print("Opening settings page...")
        # TODO: Implement navigation to settings page
        tk.messagebox.showinfo("Settings", "Opening settings page...")
        
    def open_profile(self):
        """Handle profile button click - open profile editing dialog"""
        print("Opening profile page...")
        
        # Create profile editing dialog
        profile_window = tk.Toplevel(self.root)
        profile_window.title("Edit Profile")
        profile_window.geometry("400x300")
        profile_window.configure(bg="#ffffff")
        profile_window.resizable(False, False)
        
        # Center the window
        profile_window.transient(self.root)
        profile_window.grab_set()
        
        # Title
        title_label = tk.Label(profile_window, text="Profile Information", 
                              font=("Arial", 16, "bold"), bg="#ffffff")
        title_label.pack(pady=(20, 10))
        
        # Profile form frame
        form_frame = tk.Frame(profile_window, bg="#ffffff")
        form_frame.pack(padx=20, pady=10, fill="both", expand=True)
        
        # Profile fields
        profile_fields = [
            ("Name:", "name"),
            ("Email:", "email"),
            ("Phone:", "phone"),
            ("Age:", "age")
        ]
        
        profile_entries = {}
        
        for i, (label_text, field_key) in enumerate(profile_fields):
            # Label
            label = tk.Label(form_frame, text=label_text, font=("Arial", 11, "bold"),
                           bg="#ffffff", anchor="w")
            label.grid(row=i, column=0, sticky="w", pady=8, padx=(0, 10))
            
            # Entry
            entry = tk.Entry(form_frame, font=("Arial", 11), relief="solid", bd=1)
            entry.grid(row=i, column=1, sticky="ew", pady=8)
            entry.insert(0, self.profile_data.get(field_key, ""))
            profile_entries[field_key] = entry
        
        form_frame.grid_columnconfigure(1, weight=1)
        
        # Buttons frame
        buttons_frame = tk.Frame(profile_window, bg="#ffffff")
        buttons_frame.pack(pady=20)
        
        def save_profile():
            """Save profile changes and update display"""
            # Update profile data
            for field_key, entry in profile_entries.items():
                self.profile_data[field_key] = entry.get().strip()
            
            # Update the name display in the main screen
            self.update_profile_display()
            
            tk.messagebox.showinfo("Success", "Profile updated successfully!")
            profile_window.destroy()
        
        def cancel_profile():
            """Cancel profile editing"""
            profile_window.destroy()
        
        # Save button
        save_button = tk.Button(buttons_frame, text="Save Changes",
                               font=("Arial", 11, "bold"), bg="#2196F3", fg="white",
                               width=12, height=1, command=save_profile,
                               relief="raised", bd=2)
        save_button.pack(side="left", padx=10)
        
        # Cancel button
        cancel_button = tk.Button(buttons_frame, text="Cancel",
                                 font=("Arial", 11), bg="#f44336", fg="white",
                                 width=12, height=1, command=cancel_profile,
                                 relief="raised", bd=2)
        cancel_button.pack(side="left", padx=10)
    
    def update_profile_display(self):
        """Update the profile name display in the main screen"""
        display_name = self.profile_data.get("name", "Unknown User")
        if not display_name.strip():
            display_name = "Click to set name"
        self.profile_name_label.config(text=display_name)
        
    def save_form(self):
        """Handle form save - collect and save body measurements"""
        # Collect current values from form entries
        measurements = {}
        for field_key, entry in self.form_entries.items():
            value = entry.get().strip()
            measurements[field_key] = value
        
        # Validate that all fields have values
        empty_fields = [key.replace('_', ' ').title() for key, value in measurements.items() if not value]
        
        if empty_fields:
            tk.messagebox.showwarning("Incomplete Form", 
                                    f"Please fill in the following fields:\n• {chr(10).join(empty_fields)}")
            return
        
        # Validate numeric values
        try:
            for field_key, value in measurements.items():
                if value:  # Only validate non-empty values
                    float(value)  # Check if it's a valid number
        except ValueError:
            tk.messagebox.showerror("Invalid Input", 
                                  "Please enter valid numeric values for all measurements.")
            return
        
        # Update internal data structure
        self.form_data.update(measurements)
        
        # Print the saved data (for debugging/future database integration)
        print("Saved Body Measurements:")
        for key, value in measurements.items():
            print(f"  {key.replace('_', ' ').title()}: {value} cm")
        
        # TODO: Future implementation - save to database or file
        # Example: self.save_to_database(measurements)
        # Example: self.save_to_json_file(measurements)
        
        tk.messagebox.showinfo("Success", "Body measurements saved successfully!")

    def clear_form(self):
        """Clear all form fields"""
        for entry in self.form_entries.values():
            entry.delete(0, tk.END)
        
        # Reset internal data structure
        for key in self.form_data:
            self.form_data[key] = ""
        
        print("Body measurements form cleared.")
        tk.messagebox.showinfo("Cleared", "Form cleared successfully!")
    
    def get_measurements_data(self):
        """Get current measurements data - useful for future integrations"""
        current_data = {}
        for field_key, entry in self.form_entries.items():
            current_data[field_key] = entry.get().strip()
        return current_data
    
    def load_measurements_data(self, data):
        """Load measurements data into form - useful for future integrations"""
        for field_key, value in data.items():
            if field_key in self.form_entries:
                self.form_entries[field_key].delete(0, tk.END)
                self.form_entries[field_key].insert(0, str(value))
        self.form_data.update(data)
        
    def on_closing(self):
        """Handle window closing"""
        if self.cap:
            self.cap.release()
        self.root.destroy()
>>>>>>> Stashed changes

if __name__ == "__main__":
    root = tk.Tk()
    app = MainScreen(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()