import tkinter as tk
from tkinter import ttk, messagebox
import cv2
from PIL import Image, ImageTk

class MainScreen:
    def __init__(self, root):
        self.root = root
        self.root.title("ErgoScan - Main Screen")
        self.root.geometry("1200x800")
        self.root.configure(bg="#f0f0f0")
        
        # Initialize webcam variables
        self.cap = None
        self.webcam_active = False
        
        self.setup_ui()
        self.start_webcam_preview()
        
    def setup_ui(self):
        """Set up the main user interface"""
        # Configure grid weights for responsive design
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        
        # Create left and right frames
        self.left_frame = tk.Frame(self.root, bg="#ffffff", relief="ridge", bd=2)
        self.left_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        self.right_frame = tk.Frame(self.root, bg="#ffffff", relief="ridge", bd=2)
        self.right_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        
        self.setup_left_section()
        self.setup_right_section()
        
    def setup_left_section(self):
        """Set up the left section with webcam display and start scanning button"""
        # Configure left frame grid
        self.left_frame.grid_rowconfigure(0, weight=1)
        self.left_frame.grid_columnconfigure(0, weight=1)
        
        # Title for left section
        title_label = tk.Label(self.left_frame, text="Webcam Preview", 
                              font=("Arial", 16, "bold"), bg="#ffffff")
        title_label.grid(row=0, column=0, pady=(10, 5), sticky="n")
        
        # Webcam display area
        self.webcam_frame = tk.Frame(self.left_frame, bg="#000000", 
                                   width=600, height=450, relief="sunken", bd=2)
        self.webcam_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        self.webcam_frame.grid_propagate(False)
        
        # Webcam label for displaying video feed
        self.webcam_label = tk.Label(self.webcam_frame, bg="#000000", 
                                   text="Initializing camera...", fg="white",
                                   font=("Arial", 14))
        self.webcam_label.pack(expand=True, fill="both")
        
        # Start scanning button
        self.start_button = tk.Button(self.left_frame, text="Start Scanning",
                                    font=("Arial", 14, "bold"), bg="#4CAF50", fg="white",
                                    width=20, height=2, command=self.start_scanning,
                                    relief="raised", bd=3)
        self.start_button.grid(row=2, column=0, pady=20)
        
    def setup_right_section(self):
        """Set up the right section with form, settings, and profile"""
        # Configure right frame grid
        self.right_frame.grid_rowconfigure(1, weight=1)
        self.right_frame.grid_columnconfigure(0, weight=1)
        
        # Header with icons
        header_frame = tk.Frame(self.right_frame, bg="#ffffff")
        header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        header_frame.grid_columnconfigure(0, weight=1)
        
        # Title
        title_label = tk.Label(header_frame, text="User Information", 
                              font=("Arial", 16, "bold"), bg="#ffffff")
        title_label.grid(row=0, column=0, sticky="w")
        
        # Icon buttons frame
        icons_frame = tk.Frame(header_frame, bg="#ffffff")
        icons_frame.grid(row=0, column=1, sticky="e")
        
        # Settings icon button
        self.settings_button = tk.Button(icons_frame, text="⚙️", font=("Arial", 16),
                                       width=3, height=1, command=self.open_settings,
                                       bg="#e0e0e0", relief="raised", bd=2)
        self.settings_button.pack(side="left", padx=5)
        
        # Profile icon button
        self.profile_button = tk.Button(icons_frame, text="👤", font=("Arial", 16),
                                      width=3, height=1, command=self.open_profile,
                                      bg="#e0e0e0", relief="raised", bd=2)
        self.profile_button.pack(side="left", padx=5)
        
        # Form section
        self.setup_form()
        
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
        
    def start_webcam_preview(self):
        """Start the webcam preview"""
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
        data = {}
        for key, var in self.form_vars.items():
            data[key] = var.get()
        print("Saving form data:", data)
        # TODO: Implement actual data saving
        tk.messagebox.showinfo("Success", "Information saved successfully!")
        
    def clear_form(self):
        """Clear all form fields"""
        for var in self.form_vars.values():
            var.set("")
        tk.messagebox.showinfo("Cleared", "Form cleared successfully!")
        
    def on_closing(self):
        """Handle window closing"""
        if self.cap:
            self.cap.release()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = MainScreen(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()