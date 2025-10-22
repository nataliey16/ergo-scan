import tkinter as tk
from tkinter import ttk

class ErgoScanSettings:
    def __init__(self, root):
        self.root = root
        self.root.title("ErgoScan Settings")
        self.root.geometry("900x500")
        self.root.configure(bg="#f8fafc")
        
        # Setting variables
        self.show_visual_feedback = tk.BooleanVar(value=True)
        self.audio_alert = tk.BooleanVar(value=False)
        
        # Main container
        main_frame = tk.Frame(root, bg="#f8fafc", padx=40, pady=40)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = tk.Label(
            main_frame,
            text="ErgoScan Settings",
            font=("Segoe UI", 24, "normal"),
            bg="#f8fafc",
            fg="#1e293b"
        )
        title_label.pack(anchor="w", pady=(0, 30))
        
        # Settings card
        card_frame = tk.Frame(
            main_frame,
            bg="#ffffff",
            highlightbackground="#e2e8f0",
            highlightthickness=1
        )
        card_frame.pack(fill=tk.BOTH, expand=True)
        
        # Setting 1: Show Visual Feedback
        self.create_setting_row(
            card_frame,
            "Show Visual Feedback",
            "Overlay visual alerts (e.g., red when slouching)",
            self.show_visual_feedback,
            0
        )
        
        # Separator
        separator1 = tk.Frame(card_frame, bg="#f1f5f9", height=1)
        separator1.grid(row=1, column=0, columnspan=3, sticky="ew", padx=0)
        
        # Setting 2: Audio Alert
        self.create_setting_row(
            card_frame,
            "Audio Alert (optional)",
            "Play sound when poor posture detected",
            self.audio_alert,
            2
        )
        
        # Configure grid weights for responsive layout
        card_frame.grid_columnconfigure(0, weight=1, minsize=200)
        card_frame.grid_columnconfigure(1, weight=2, minsize=300)
        card_frame.grid_columnconfigure(2, weight=1, minsize=150)
        
        # Settings Summary
        summary_frame = tk.Frame(
            main_frame,
            bg="#ffffff",
            highlightbackground="#e2e8f0",
            highlightthickness=1
        )
        summary_frame.pack(fill=tk.X, pady=(20, 0))
        summary_frame.configure(padx=20, pady=20)
        
        summary_title = tk.Label(
            summary_frame,
            text="Current Settings:",
            font=("Segoe UI", 11, "normal"),
            bg="#ffffff",
            fg="#475569"
        )
        summary_title.pack(anchor="w")
        
        # Visual Feedback status
        self.visual_feedback_status = tk.Label(
            summary_frame,
            text="",
            font=("Segoe UI", 10),
            bg="#ffffff",
            fg="#475569"
        )
        self.visual_feedback_status.pack(anchor="w", pady=(5, 2))
        
        # Audio Alert status
        self.audio_alert_status = tk.Label(
            summary_frame,
            text="",
            font=("Segoe UI", 10),
            bg="#ffffff",
            fg="#475569"
        )
        self.audio_alert_status.pack(anchor="w")
        
        # Update status initially
        self.update_status()
    
    def create_setting_row(self, parent, setting_name, purpose, variable, row):
        """Create a setting row with three columns"""
        # Column 1: Setting Name
        name_label = tk.Label(
            parent,
            text=setting_name,
            font=("Segoe UI", 11, "normal"),
            bg="#ffffff",
            fg="#1e293b",
            anchor="w"
        )
        name_label.grid(row=row, column=0, sticky="w", padx=25, pady=25)
        
        # Column 2: Purpose
        purpose_label = tk.Label(
            parent,
            text=purpose,
            font=("Segoe UI", 10),
            bg="#ffffff",
            fg="#64748b",
            anchor="w",
            wraplength=300,
            justify="left"
        )
        purpose_label.grid(row=row, column=1, sticky="w", padx=25, pady=25)
        
        # Column 3: Checkbox with label
        checkbox_frame = tk.Frame(parent, bg="#ffffff")
        checkbox_frame.grid(row=row, column=2, sticky="w", padx=25, pady=25)
        
        # Custom styled checkbox
        checkbox = tk.Checkbutton(
            checkbox_frame,
            variable=variable,
            command=self.update_status,
            bg="#ffffff",
            activebackground="#ffffff",
            highlightthickness=0,
            borderwidth=0,
            font=("Segoe UI", 10),
            cursor="hand2"
        )
        checkbox.pack(side=tk.LEFT)
        
        checkbox_label = tk.Label(
            checkbox_frame,
            text="Checkbox",
            font=("Segoe UI", 9),
            bg="#ffffff",
            fg="#94a3b8"
        )
        checkbox_label.pack(side=tk.LEFT, padx=(5, 0))
        
        # Bind hover effect
        name_label.bind("<Enter>", lambda e: self.on_row_enter(parent, row))
        purpose_label.bind("<Enter>", lambda e: self.on_row_enter(parent, row))
        checkbox_frame.bind("<Enter>", lambda e: self.on_row_enter(parent, row))
        
        name_label.bind("<Leave>", lambda e: self.on_row_leave(parent, row))
        purpose_label.bind("<Leave>", lambda e: self.on_row_leave(parent, row))
        checkbox_frame.bind("<Leave>", lambda e: self.on_row_leave(parent, row))
    
    def on_row_enter(self, parent, row):
        """Change background on hover"""
        for widget in parent.grid_slaves(row=row):
            if isinstance(widget, tk.Label):
                widget.configure(bg="#f8fafc")
            elif isinstance(widget, tk.Frame):
                widget.configure(bg="#f8fafc")
                for child in widget.winfo_children():
                    if isinstance(child, (tk.Checkbutton, tk.Label)):
                        child.configure(bg="#f8fafc")
                        if isinstance(child, tk.Checkbutton):
                            child.configure(activebackground="#f8fafc")
    
    def on_row_leave(self, parent, row):
        """Restore background on leave"""
        for widget in parent.grid_slaves(row=row):
            if isinstance(widget, tk.Label):
                widget.configure(bg="#ffffff")
            elif isinstance(widget, tk.Frame):
                widget.configure(bg="#ffffff")
                for child in widget.winfo_children():
                    if isinstance(child, (tk.Checkbutton, tk.Label)):
                        child.configure(bg="#ffffff")
                        if isinstance(child, tk.Checkbutton):
                            child.configure(activebackground="#ffffff")
    
    def update_status(self):
        """Update the status summary"""
        # Visual Feedback status
        vf_status = "Enabled" if self.show_visual_feedback.get() else "Disabled"
        vf_color = "#059669" if self.show_visual_feedback.get() else "#dc2626"
        self.visual_feedback_status.config(
            text=f"Visual Feedback: {vf_status}",
            fg=vf_color
        )
        
        # Audio Alert status
        aa_status = "Enabled" if self.audio_alert.get() else "Disabled"
        aa_color = "#059669" if self.audio_alert.get() else "#dc2626"
        self.audio_alert_status.config(
            text=f"Audio Alerts: {aa_status}",
            fg=aa_color
        )
    
    def get_settings(self):
        """Return current settings as a dictionary"""
        return {
            "show_visual_feedback": self.show_visual_feedback.get(),
            "audio_alert": self.audio_alert.get()
        }


def main():
    root = tk.Tk()
    app = ErgoScanSettings(root)
    root.mainloop()


if __name__ == "__main__":
    main()
